"""Compile and run the app's forecast JSON parser with its real Java libraries."""

import fcntl
import hashlib
import io
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import urllib.request
import zipfile


DEPENDENCIES = [
    ('gson.jar', 'https://repo.maven.apache.org/maven2/com/google/code/gson/gson/2.13.2/gson-2.13.2.jar',
     'dd0ce1b55a3ed2080cb70f9c655850cda86c206862310009dcb5e5c95265a5e0'),
    ('annotations.jar', 'https://dl.google.com/dl/android/maven2/androidx/annotation/annotation-jvm/1.9.1/annotation-jvm-1.9.1.jar',
     '1e343917ebf27ba96fe4dc52b1cad7fd32b738fbc6355bb6cd5b3b305d7212d0')]
JAVA_HOME = Path('/usr/lib/jvm/java-21-openjdk-amd64')
TOOLS_URL = 'https://dl.google.com/android/repository/commandlinetools-linux-16111833_latest.zip'
TOOLS_SHA256 = '0877a1d048fe4a24efe2eff536ca4223f7adeb58648bb81909d33c446918cfa8'


def java_environment():
    """Select the profile's JDK 21 even when the runner puts older Java on PATH."""
    for tool in ['java', 'javac']:
        result = subprocess.run([str(JAVA_HOME / 'bin' / tool), '--version'],
                                capture_output=True, text=True, timeout=30)
        assert result.returncode == 0, result.stdout + result.stderr
        assert result.stdout.split()[1].split('.')[0] == '21', result.stdout
    return dict(os.environ, JAVA_HOME=str(JAVA_HOME),
                PATH=str(JAVA_HOME / 'bin') + os.pathsep + os.environ['PATH'])


def pinned_sdkmanager(cache):
    """Use verified CLI 23.0 from our cache without replacing the runner's SDK tools."""
    bundle = cache / 'commandlinetools-16111833.zip'
    if not bundle.exists():
        with urllib.request.urlopen(TOOLS_URL, timeout=90) as response:
            data = response.read()
        assert hashlib.sha256(data).hexdigest() == TOOLS_SHA256
        bundle.write_bytes(data)
    data = bundle.read_bytes()
    assert hashlib.sha256(data).hexdigest() == TOOLS_SHA256
    tools = cache / 'commandlinetools-16111833'
    if not tools.exists():
        with tempfile.TemporaryDirectory(dir=cache) as stage:
            with zipfile.ZipFile(io.BytesIO(data)) as archive:
                archive.extractall(stage)
            shutil.move(str(Path(stage) / 'cmdline-tools'), tools)
        for executable in (tools / 'bin').iterdir():
            executable.chmod(0o755)
    assert 'Pkg.Revision=23.0' in (tools / 'source.properties').read_text()
    return tools / 'bin/sdkmanager'


def test_forecast_json_round_trip(payload, tmp_path):
    env = java_environment()
    jars = []
    for name, url, digest in DEPENDENCIES:
        with urllib.request.urlopen(url, timeout=30) as response:
            data = response.read()
        assert hashlib.sha256(data).hexdigest() == digest
        jar = tmp_path / name
        jar.write_bytes(data)
        jars.append(str(jar))
    source = payload / 'app/src/main/java/com/odiousapps/weewxweather'
    harness = tmp_path / 'ForecastParserCheck.java'
    harness.write_text(r'''package com.odiousapps.weewxweather;
public class ForecastParserCheck {
    public static void main(String[] args) {
        GsonHelper forecast = new GsonHelper("{\"desc\":\"Fixture\",\"timestamp\":1751457600,\"isDaily\":true,\"days\":[{\"max\":\"0\",\"min\":\"-2\",\"text\":\"Rain & frost\",\"timestamp\":1751457600}]}");
        if (forecast.timestamp != 1751457600L || !forecast.isDaily)
            throw new AssertionError("Forecast timestamp or daily flag lost");
        if (forecast.days.size() != 1 || !forecast.days.get(0).max.equals("0"))
            throw new AssertionError("Zero temperature lost");
        GsonHelper roundTrip = new GsonHelper(forecast.toString());
        if (!roundTrip.days.get(0).text.equals("Rain & frost"))
            throw new AssertionError("Forecast text changed");
        GsonHelper missing = new GsonHelper("{}");
        if (!missing.desc.equals("") || missing.timestamp != 0 || missing.isDaily)
            throw new AssertionError("Missing-field defaults changed");
        System.out.println("forecast-parser-ok");
    }
}
''')
    classpath = os.pathsep.join(jars)
    compiled = subprocess.run([str(JAVA_HOME / 'bin/javac'), '--release', '21', '-cp', classpath, '-d', str(tmp_path),
                              str(source / 'Day.java'), str(source / 'GsonHelper.java'), str(harness)],
                             env=env, capture_output=True, text=True, timeout=60)
    assert compiled.returncode == 0, compiled.stdout + compiled.stderr
    executed = subprocess.run([str(JAVA_HOME / 'bin/java'), '-cp', classpath + os.pathsep + str(tmp_path),
                               'com.odiousapps.weewxweather.ForecastParserCheck'],
                              env=env, capture_output=True, text=True, timeout=30)
    assert executed.returncode == 0, executed.stdout + executed.stderr
    assert 'forecast-parser-ok' in executed.stdout


def test_android_debug_build(payload, tmp_path):
    """Build the archived app with JDK 21 and the verified CLI's SDK 37.0 packages."""
    cache = Path(os.environ.get('RUNNER_TEMP', tempfile.gettempdir())) / 'weewx-weather-app-tools'
    cache.mkdir(exist_ok=True)
    sdk_hint = os.environ.get('ANDROID_HOME') or os.environ.get('ANDROID_SDK_ROOT')
    sdk = Path(sdk_hint) if sdk_hint else cache / 'sdk'
    env = dict(java_environment(), ANDROID_HOME=str(sdk), ANDROID_SDK_ROOT=str(sdk),
               GRADLE_USER_HOME=str(cache / 'gradle'))
    with (cache / 'sdk.lock').open('w') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        manager = pinned_sdkmanager(cache)
        if not (sdk / 'platforms/android-37.0/android.jar').is_file() or not (sdk / 'build-tools/37.0.0/aapt2').is_file():
            installed = subprocess.run([str(manager), '--sdk_root=' + str(sdk),
                'platforms/android-37.0', 'build-tools/37.0.0', 'platform-tools'],
                input='y\n' * 30, env=env, capture_output=True, text=True, timeout=720)
            assert (installed.returncode == 0
                    and (sdk / 'platforms/android-37.0/android.jar').is_file()
                    and (sdk / 'build-tools/37.0.0/aapt2').is_file()), installed.stdout + installed.stderr
    build = subprocess.run(['bash', str(payload / 'gradlew'), '--project-dir', str(payload),
                            '-Dorg.gradle.java.home=' + str(JAVA_HOME), '--no-daemon',
                            '--max-workers=2', 'testDebugUnitTest', 'assembleDebug'],
                           cwd=payload, env=env, capture_output=True, text=True, timeout=720)
    (tmp_path / 'android-build.log').write_text(build.stdout + build.stderr)
    assert build.returncode == 0, build.stdout + build.stderr
    apk = payload / 'app/build/outputs/apk/debug/app-debug.apk'
    assert apk.is_file() and apk.stat().st_size > 1000000
    with zipfile.ZipFile(apk) as archive:
        assert 'AndroidManifest.xml' in archive.namelist()
        assert 'classes.dex' in archive.namelist()

<?php
// WordPress owns HTTP, options and cache storage. Keep those boundaries local.
define('ABSPATH', __DIR__ . '/');
class WPWeeWX_Settings {
    public static function sanitize_source($source) { return $source; }
    public static function get($name) {
        return ['wpweewx_json_url_main' => 'https://example.invalid/current.json',
                'wpweewx_http_timeout' => 5, 'wpweewx_cache_ttl' => 60][$name] ?? '';
    }
    public static function get_temp_unit() { return 'c'; }
    public static function get_source_temp_unit() { return 'f'; }
}
function __($text, $domain) { return $text; }
function wp_parse_url($url) { return parse_url($url); }
function is_wp_error($response) { return false; }
function wp_remote_get($url, $args) {
    $GLOBALS['requests'][] = [$url, $args];
    return ['code' => $GLOBALS['status'], 'body' => $GLOBALS['body']];
}
function wp_remote_retrieve_response_code($response) { return $response['code']; }
function wp_remote_retrieve_body($response) { return $response['body']; }
function get_transient($key) { return $GLOBALS['cache'][$key] ?? false; }
function set_transient($key, $value, $ttl) { $GLOBALS['cache'][$key] = $value; }
function add_query_arg($key, $value, $url) { return $url . '?' . $key . '=' . $value; }
function number_format_i18n($value, $precision) { return number_format($value, $precision, '.', ','); }
require $argv[1] . '/includes/class-wpweewx-parser.php';
require $argv[1] . '/includes/class-wpweewx-fetcher.php';
require $argv[1] . '/includes/class-wpweewx-renderer.php';
$GLOBALS['status'] = 200;
$GLOBALS['body'] = '{"current":{"temperature":{"value":68,"unit":"degree_F"},"rain":0,"missing": },"empty":[1,,3,]}';
$GLOBALS['requests'] = [];
$result = WPWeeWX_Fetcher::get_data('main');
$cached = WPWeeWX_Fetcher::get_data('main');
$GLOBALS['status'] = 503;
$stale = WPWeeWX_Fetcher::get_data('main', true);
echo json_encode([
    'zero' => WPWeeWX_Parser::get($result['data'], 'current.rain'),
    'missing' => WPWeeWX_Parser::get($result['data'], 'current.missing'),
    'array' => $result['data']['empty'],
    'temperature' => WPWeeWX_Renderer::display_value($result['data'], 'current.temperature'),
    'cached' => $cached['cache_used'], 'stale' => $stale['cache_used'],
    'warning' => $stale['warning'], 'requests' => count($GLOBALS['requests']),
]);

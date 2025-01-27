<?php
define('CLI_SCRIPT', true);

$returnvalue = [];

// Check for config.php
if (!file_exists(__DIR__ . '/../../config.php')) {
    $returnvalue = [
        'failed' => false,
        'msg' => 'Config file not found',
        'moodle_is_installed' => false,
    ];
    echo json_encode($returnvalue);
    exit(0);
}

require(__DIR__ . '/../../config.php');
require_once($CFG->libdir . '/clilib.php');
require_once($CFG->libdir . '/adminlib.php');
require_once($CFG->libdir . '/upgradelib.php');

$moodleneedsupgrade = moodle_needs_upgrading();

$returnvalue = [
    'failed' => false,
    'moodle_is_installed' => true,
    'moodle_needs_upgrading' => $moodleneedsupgrade,
    'current_version' => $CFG->version,
    'current_release' => $CFG->release,
];

echo json_encode($returnvalue);
exit(0);


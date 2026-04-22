<?php
define('CLI_SCRIPT', true);

try {
    $returnvalue = [];

    if (empty($_SERVER['argv'])) {
        die('This script is intended to be run from the command line');
    }
    $rawoptions = $_SERVER['argv'];
    $cfgpath = './';
    if ($_SERVER['argc'] >= 2) {
        $cfgpath = $rawoptions[1];
    }

    // Check for config.php
    $configpath = rtrim($cfgpath, '/') . '/config.php';
    if (file_exists($configpath)) {
        require($configpath);
    } else {
        $returnvalue = [
            'failed' => true,
            'msg' => 'Config file not found',
        ];
        echo json_encode($returnvalue);
        exit(0);
    }
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
} catch (Exception $e) {
    if (in_array(get_class($e), ['dml_connection_exception', 'dml_read_exception', 'dml_exception'])) {
        $returnvalue = [
            'failed' => false,
            'moodle_is_installed' => false,
            'moodle_needs_upgrading' => false,
            'current_version' => 'Unknown',
            'current_release' => 'Unknown',
        ];
    } else {
        $returnvalue = [
            'failed' => true,
            'msg' => $e->getMessage(),
        ];
    }
    echo json_encode($returnvalue);
}
exit(0);

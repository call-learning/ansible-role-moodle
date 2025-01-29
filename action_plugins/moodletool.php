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
    if (file_exists($cfgpath . '/config.php')) {
        require($cfgpath . '/config.php');
    } else {
        $returnvalue = [
            'failed' => true,
            'msg' => 'Config file not found',
            'moodle_is_installed' => false,
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
    $returnvalue = [
        'failed' => true,
        'msg' => $e->getMessage(),
        'moodle_is_installed' => false,
    ];
    echo json_encode($returnvalue);
}
exit(0);

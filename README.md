# Tracker of Detergent Usage
**What:** This app has been created to track usage of your detergent.\
**Why:** In case someone were to systematically snatches it.

Before using the app, I strongly advice to fill the config file (`CONFIG.json`) and attach it, otherwise the app will work in an unexpected way or not run at all. The following options are available:
```json
{
  "bottle_volume": <number > 0>,
  "cup_colume": <number > 0>
}
```

(Unit of volume: whatever as long as consistent over all parameters.)

Adding other options will result in an error, which can be fixed automatically by using `--reset` flag and resetting the config.
Or manually by reverting changes.

**The following features are implemented:**
-	Enter the number of cups of detergent used in the last wash.
-	See the current (expected) usage of the detergent
-	Delete all or select which data to delete.
-	Get help

**Usage:**
Call the app with `docker <flag(s)> <values>`
* `-h` (`--help`) - get help
* `-l` (`--log`) `<n-cups>` - input the number of cups used in the last wash
* `-s` (`--status`) - show a status report of the current detergent
* `--reset` - reset data to defaults

You can only use ONE flag per call. The only exception is `--log <n-cups> --status`.\
For example: call `docker <flag(s)> --log 0.5` to log that you've used 0.5 cups of detergent in your most current wash

**WARNING** The app is untested. And although a lot of edge cases have been thought of during the SDLC phase, errors and / unexpected behavior may still be present

P.S. - The date format is DD.MM.YYYY.
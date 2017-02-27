# giftplayer, a handy GIFT quiz player

Gift format is a text format for quiz [document](https://docs.moodle.org/23/en/GIFT_format) of Moodle CMS.

`giftpalayer` is a quick checking tool for quiz written in Gift format.

Usage 1: Generate a HTML document for a given Gift quiz.

```sh
$ echo '::Q1:: Two times three equals {=six =6}' | python3 giftplay_run.py - | bcat
```

Usage 2: Run a web server for a given gift quiz.

```sh
$ echo '::Q1:: Two times three equals {=six =6}' | python3 giftplay_run.py -w -
```

![screenshot](https://cloud.githubusercontent.com/assets/1262286/23339329/61293a0c-fc63-11e6-85fa-ccb2a2b04d60.jpg)

## License

BSD-3-Clause, except for an enclosed `jquery-*.js` file.

# giftplayer, a hany GIFT quiz player

Gift format is a text format for quiz [document](https://docs.moodle.org/23/en/GIFT_format) of Moodle CMS.

`giftpalayer` is a quick checking tool for quiz written in Gift format.

```sh
$ cat q.gift
::Q1:: Two times three equals {=six =6}.
$ python3 giftplayer_run.py cat q.gift
```

![screenshot](https://cloud.githubusercontent.com/assets/1262286/23262779/3a286298-fa1f-11e6-8686-16cb31643d59.jpg)

## License

BSD-3-Clause, except for an enclosed `jquery-*.js` file.

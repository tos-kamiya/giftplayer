# giftplayer, a hany GIFT quiz player

Gift format is a text format for quiz [document](https://docs.moodle.org/23/en/GIFT_format) of Moodle CMS.

`giftpalayer` is a quick checking tool for quiz written in Gift format.

```sh
$ cat q.gift
::Q1:: Two times three equals {=six =6}.
$ python3 giftplayer_run.py html q.gift | bcat
```

## License

BSD-3-Clause, except for an enclosed `jquery-*.js` file.

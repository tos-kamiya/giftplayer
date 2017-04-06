# giftplayer, a handy GIFT quiz player

Gift format is a text format for quiz [document](https://docs.moodle.org/23/en/GIFT_format) of Moodle CMS.

`giftpalayer` is a quick checking tool for quiz written in Gift format.

Usage 1: Generate a HTML document for a given Gift quiz.

```sh
$ echo '::Q1:: Two times three equals {=six =6}' | giftplayer_run cat - | bcat
```

Here, [bcat](https://rtomayko.github.io/bcat/) is a HTML viewer (if you are using Ubuntu, it can be installed with `apt install ruby-bcat`).

Usage 2: Run a web server for a given Gift quiz.

```sh
$ echo '::Q1:: Two times three equals {=six =6}' | giftplayer_run web -
```

![screenplay](images/screenplay.gif)

## Installation

Just to try it, clone the repository & run it like:

```sh
$ git clone https://github.com/tos-kamiya/giftplayer
$ cd giftplayer
$ ./giftplayer_run cat giftplayer/sample.gift
<!DOCTYPE html>
<html>
....
```

To install, run `sudo pip3 install git+https://github.com/tos-kamiya/giftplayer`.

## CLI usage

```
Usage:
  giftplayer_run cat [options] <giftscript>
  giftplayer_run web [options] <giftscript>
  giftplayer_run (--help|--version)

Options:
  -s <seed> --shuffle=<seed>  Seed of shuffling choices of each question.
  -p <port> --port=<PORT>     Port number of web app', [default: 5000].
  --debug-wo-hint             Debug option. Generate HTML w/o parsing answer.
```

## Supported rules of GIFT syntax

See [sample.gift](giftplay/sample.gift).

Supported:

* true/false
* multiple choice
* fill-in-the-blank
* matching
* math range
* math range specified with interval end points
* essay
* multiple choice with multiple right answers

Not yet supported:

* multiple numeric answers

## License

BSD-3-Clause, except for an enclosed `jquery-*.js` file.

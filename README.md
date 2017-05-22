# giftplayer, a handy GIFT quiz player

Gift format is a text format for quiz [document](https://docs.moodle.org/23/en/GIFT_format) of Moodle CMS.

`giftpalayer` is a quick checking tool for quiz written in Gift format.

Usage 1: Generate an HTML document for a given Gift quiz.

```sh
$ echo '::Q1:: Two times three equals {=six =6}' | giftplayer cat - | bcat
```

Here, [bcat](https://rtomayko.github.io/bcat/) is a HTML viewer (if you are using Ubuntu, it can be installed with `apt install ruby-bcat`).

Usage 2: Run a web server for a given Gift quiz.

```sh
$ echo '::Q1:: Two times three equals {=six =6}' | giftplayer web -
```

![screenplay](images/screenplay.gif)

## Installation

Just to try it, clone the repository & run it like:

```sh
$ git clone https://github.com/tos-kamiya/giftplayer
$ cd giftplayer
$ ./giftplayer cat samples/sample_quiz.gift
<!DOCTYPE html>
<html>
....
```

To install, run `sudo pip3 install git+https://github.com/tos-kamiya/giftplayer`.

To uninstall, run `sudo pip3 uninstall giftplayer` .

## CLI usage

```
Usage:
  giftplayer cat [options] <giftscript>
  giftplayer web [options] <giftscript>
  giftplayer (--help|--version)

Options:
  -s <seed> --shuffle=<seed>  Seed of shuffling choices of each question.
  -p <port> --port=<PORT>     Port number of web app', [default: 5000].
  --debug-wo-hint             Debug option. Generate HTML w/o parsing answer.
```

## Troubleshooting

**Q**: I am writing a gift file `some-quiz.gift`. When I modify the file and then run `giftplayer web some-quiz.gift`, **the page content does not look updated** (even I reload the page with a `reload` button of a browser), showing the old content. Why?

**A**: An HTML page cashing is sometime not controllable. To avoid caching, add some path to the URL like: `http://localhost:5000/foo_bar` (`foo_bar` or any word you like). `giftplayer` server will show the quiz page for any path except for `/submit_answer`.

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

* feedback
* multiple numeric answers

## License

BSD-3-Clause, except for an enclosed `jquery-*.js` file.

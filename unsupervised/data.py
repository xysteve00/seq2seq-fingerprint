"""Prepare data for seq2seq training."""

from __future__ import print_function

import os
import tempfile
import tensorflow as tf

from .utils import get_vocabulary, smile_tokenizer, data_to_token_ids


tf.app.flags.DEFINE_string(
    "smi_path", "/smile/nfs/projects/nih_drug/data/logp/logp.smi", "smi data path.")
tf.app.flags.DEFINE_string(
    "tmp_path", "", "Temporary data path. If none, a named temporary file will be used.")
tf.app.flags.DEFINE_string(
    "vocab_path", "", "Vocabulary data_path.")
tf.app.flags.DEFINE_string(
    "out_path", "", "Output token path.")
tf.app.flags.DEFINE_bool(
    "build_vocab", False, "Trigger the action: False for translating only. "
    "If true, the script will build vocabulary and then translating.")

FLAGS = tf.app.flags.FLAGS

def mkdirp(dir_path):
    """Error-free version of os.makedirs."""
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)

def norm_path(ori_path):
    """Normalize path."""
    return os.path.expanduser(os.path.expandvars(ori_path))

def smi_data_iter(smi_path=FLAGS.smi_path):
    """Yield logp SMILE representation."""
    with open(smi_path) as fobj:
        for line in fobj:
            leng_line_strip = len(line.strip())
            if not leng_line_strip:
                continue
            _smile = line.strip().split()[0]
            yield _smile

def build_data_tmp(data_iter, data_path):
    """Build temp data file inside the data_directory. This is required for tensorflow function."""
    with open(data_path, "w+") as fobj:
        for _smile in data_iter:
            fobj.write("%s\n" % _smile)

def check_output_path(path):
    """Create folder if not exists."""
    dir_path = os.path.dirname(path)
    mkdirp(dir_path)
    return dir_path

def assert_path_exists(path):
    """Make sure the path exists."""
    assert os.path.exists(path), "Path does not exist: %s" % path

def build_vocab(smi_path=FLAGS.smi_path,
                vocab_path=FLAGS.vocab_path,
                out_path=FLAGS.out_path):
    """Build vocabulary for the given data."""
    # create folder if needed.
    assert_path_exists(smi_path)
    check_output_path(vocab_path)
    if out_path:
        check_output_path(out_path)

    with tempfile.NamedTemporaryFile() as tmp_file:
        tmp_path = FLAGS.tmp_path or tmp_file.name

        data_iter = smi_data_iter(smi_path)
        print("Creating temp file...")
        build_data_tmp(data_iter, tmp_path)
        print("Building vocabulary...")
        get_vocabulary(tmp_path, vocab_path)
        if out_path:
            print("Translating vocabulary to tokens...")
            data_to_token_ids(tmp_path, out_path, vocab_path,
                              tokenizer=smile_tokenizer, normalize_digits=False)

def translate_tokens(smi_path=FLAGS.smi_path,
                     vocab_path=FLAGS.vocab_path,
                     out_path=FLAGS.out_path):
    """Output tokens from given vocab."""
    assert_path_exists(smi_path)
    assert_path_exists(vocab_path)
    check_output_path(out_path)

    with tempfile.NamedTemporaryFile() as tmp_file:
        tmp_path = FLAGS.tmp_path or tmp_file.name

        data_iter = smi_data_iter(smi_path)
        print("Creating temp file...")
        build_data_tmp(data_iter, tmp_path)
        print("Reading vocabulary...")
        get_vocabulary(tmp_path, vocab_path)
        print("Translating vocabulary to tokens...")
        data_to_token_ids(tmp_path, out_path, vocab_path,
                          tokenizer=smile_tokenizer, normalize_digits=False)

def main(_):
    """Entry function for this script."""
    if FLAGS.build_vocab:
        build_vocab()
    else:
        translate_tokens()

if __name__ == "__main__":
    tf.app.run()

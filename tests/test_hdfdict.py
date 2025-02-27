#from pytest import assert
import os
import numpy as np
import h5py
import hdfdict
import datetime


d = {
    'a': np.random.randn(10),
    'b': [1, 2, 3],
    'c': 'Hallo',
    'd': np.array(['a', 'b']).astype('S'),
    'e': True,
    'f': (True, False),
}
fname = 'test_hdfdict.h5'


def test_dict_to_hdf():
    if os.path.isfile(fname):
        os.unlink(fname)
    hdfdict.dump(d, fname, "w")
    for lazy in [True, False]:
        res = hdfdict.load(fname, lazy=lazy)
        assert(np.all(d['a'] == res['a']))
        assert(np.all(d['b'] == res['b']))
        assert(np.all(d['c'] == res['c'].decode()))
        assert(tuple(d.keys()) == tuple(res.keys()))


def test_dict_to_hdf_with_datetime():
    d = {
        'e': [datetime.datetime.now() for i in range(3)],
        'f': datetime.datetime.utcnow(),
        'g': [('Hello', 5), (6, 'No HDF but json'), ('foo', True)],
        'h': {'test2': datetime.datetime.now(), 
              'again': ['a', 1], (1, 2): (3, 4)}
    }
    fname = 'test_hdfdict.h5'
    if os.path.isfile(fname):
        os.unlink(fname)
    hf = h5py.File(fname, "w")
    hdfdict.dump(d, hf)
    res = hdfdict.load(hf, lazy=False)
    res = hdfdict.load(hf)
    res.unlazy()  # all lazy objects will be rolled out.
    def equaldt(a, b):
        d = a - b
        return d.total_seconds() < 1e-3

    assert(all([equaldt(a, b) for (a, b) in zip(d['e'], res['e'])]))
    assert(equaldt(d['f'], res['f']))
    assert(d['g'][0][0] == 'Hello')
    assert(d['g'][1][0] == 6)
    assert(d.keys() == res.keys())
    assert(isinstance(res['h']['test2'], datetime.datetime))
    assert(res['h']['again'][0]=='a')
    assert(res['h']['again'][1]==1)
    hf.close()

    if os.path.isfile(fname):
        os.unlink(fname)


if __name__ == '__main__':
    import pytest

    pytest.main()
    if os.path.isfile(fname):
        os.unlink(fname)

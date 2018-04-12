#This file is part of QNET.
#
#    QNET is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#    QNET is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with QNET.  If not, see <http://www.gnu.org/licenses/>.
#
# Copyright (C) 2012-2017, QNET authors (see AUTHORS file)
#
###########################################################################


from qnet.algebra.circuit_algebra import (
    Concatenation, SeriesProduct, CPermutation, CircuitSymbol, cid, Feedback,
    SLH)
from qnet.algebra.operator_algebra import Create, Destroy
from qnet.algebra.matrix_algebra import Matrix, identity_matrix
from qnet.visualization.circuit_pyx import draw_circuit
from os import path, remove
from tempfile import gettempdir
import pyx

import unittest


class TestVisualizationPNG(unittest.TestCase):

    def setUp(self):
        self.fname = gettempdir()  + '/tmp.png'

    def tearDown(self):
        if path.exists(self.fname):
            remove(self.fname)

    def testPyX(self):

        if path.exists(self.fname):
            remove(self.fname)

        c = pyx.canvas.canvas()

        c.text(0, 0, "Hello, world!")
        c.stroke(pyx.path.line(0, 0, 2, 0))
        c.writeGSfile(self.fname)
        self.assertTrue(path.exists(self.fname))
        remove(self.fname)


    def assertCanBeDrawn(self, circuit):

        if path.exists(self.fname):
            remove(self.fname)

        self.assertTrue(draw_circuit(circuit, self.fname, 'lr'))
        self.assertTrue(path.exists(self.fname))
        remove(self.fname)

        self.assertTrue(draw_circuit(circuit, self.fname, 'rl'))
        self.assertTrue(path.exists(self.fname))
        remove(self.fname)

    def testDrawSymbol(self):
        self.assertCanBeDrawn(CircuitSymbol('b',1))
        self.assertCanBeDrawn(CircuitSymbol('b',2))

    def testDrawCPermutation(self):
        self.assertCanBeDrawn(CPermutation((0,2,3,1)))

    def testDrawSeries(self):
        self.assertCanBeDrawn(SeriesProduct(CircuitSymbol('a',5),CircuitSymbol('b',5)))

    def testDrawConcatenation(self):
        self.assertCanBeDrawn(Concatenation(CircuitSymbol('a', 5), CircuitSymbol('b', 5)))

    def testDrawIdentity(self):
        self.assertCanBeDrawn(cid(5))

    def testDrawFeedback(self):
        self.assertCanBeDrawn(Feedback(CircuitSymbol('M',5), out_port=3, in_port=4))

    def testDrawNested(self):
        self.assertCanBeDrawn(SeriesProduct(CircuitSymbol('a',2),Concatenation(CircuitSymbol('b',1), CircuitSymbol('c',1))))
        self.assertCanBeDrawn(Concatenation(CircuitSymbol('a',2),SeriesProduct(CircuitSymbol('b',1), CircuitSymbol('c',1))))
        self.assertCanBeDrawn(Feedback(Concatenation(CircuitSymbol('a',2),SeriesProduct(CircuitSymbol('b',1), CircuitSymbol('c',1))), out_port=2, in_port=0))

    def testDrawSLH(self):
        self.assertCanBeDrawn(SLH(identity_matrix(1), Matrix([[Create(hs=1)]]), Create(hs=1)*Destroy(hs=1)))


class TestVisualizationEPS(unittest.TestCase):
    def setUp(self):
        self.fname = gettempdir() + '/tmp.eps'

    def tearDown(self):
        if path.exists(self.fname):
            remove(self.fname)

    def testPyX(self):
        if path.exists(self.fname):
            remove(self.fname)

        c = pyx.canvas.canvas()

        c.text(0, 0, "Hello, world!")
        c.stroke(pyx.path.line(0, 0, 2, 0))
        c.writeEPSfile(self.fname)
        self.assertTrue(path.exists(self.fname))
        remove(self.fname)


    def assertCanBeDrawn(self, circuit):
        if path.exists(self.fname):
            remove(self.fname)

        self.assertTrue(draw_circuit(circuit, self.fname, 'lr'))
        self.assertTrue(path.exists(self.fname))
        remove(self.fname)

        self.assertTrue(draw_circuit(circuit, self.fname, 'rl'))
        self.assertTrue(path.exists(self.fname))
        remove(self.fname)

    def testDrawSymbol(self):
        self.assertCanBeDrawn(CircuitSymbol('b', 1))
        self.assertCanBeDrawn(CircuitSymbol('b', 2))

    def testDrawCPermutation(self):
        self.assertCanBeDrawn(CPermutation((0, 2, 3, 1)))

    def testDrawSeries(self):
        self.assertCanBeDrawn(SeriesProduct(CircuitSymbol('a', 5), CircuitSymbol('b', 5)))

    def testDrawConcatenation(self):
        self.assertCanBeDrawn(Concatenation(CircuitSymbol('a', 5), CircuitSymbol('b', 5)))

    def testDrawIdentity(self):
        self.assertCanBeDrawn(cid(5))

    def testDrawFeedback(self):
        self.assertCanBeDrawn(Feedback(CircuitSymbol('M', 5), out_port=3, in_port=4))

    def testDrawNested(self):
        self.assertCanBeDrawn(
            SeriesProduct(CircuitSymbol('a', 2), Concatenation(CircuitSymbol('b', 1), CircuitSymbol('c', 1))))
        self.assertCanBeDrawn(
            Concatenation(CircuitSymbol('a', 2), SeriesProduct(CircuitSymbol('b', 1), CircuitSymbol('c', 1))))
        self.assertCanBeDrawn(
            Feedback(Concatenation(CircuitSymbol('a', 2), SeriesProduct(CircuitSymbol('b', 1), CircuitSymbol('c', 1))),
                out_port=2, in_port=0))

    def testDrawSLH(self):
        self.assertCanBeDrawn(SLH(identity_matrix(1), Matrix([[Create(hs=1)]]), Create(hs=1) * Destroy(hs=1)))



class TestVisualizationPDF(unittest.TestCase):
    def setUp(self):
        self.fname = gettempdir() + '/tmp.pdf'

    def tearDown(self):
        if path.exists(self.fname):
            remove(self.fname)

    def testPyX(self):
        if path.exists(self.fname):
            remove(self.fname)

        c = pyx.canvas.canvas()

        c.text(0, 0, "Hello, world!")
        c.stroke(pyx.path.line(0, 0, 2, 0))
        c.writePDFfile(self.fname)
        self.assertTrue(path.exists(self.fname))
        remove(self.fname)


    def assertCanBeDrawn(self, circuit):
        if path.exists(self.fname):
            remove(self.fname)

        self.assertTrue(draw_circuit(circuit, self.fname, 'lr'))
        self.assertTrue(path.exists(self.fname))
        remove(self.fname)

        self.assertTrue(draw_circuit(circuit, self.fname, 'rl'))
        self.assertTrue(path.exists(self.fname))
        remove(self.fname)

    def testDrawSymbol(self):
        self.assertCanBeDrawn(CircuitSymbol('b', 1))
        self.assertCanBeDrawn(CircuitSymbol('b', 2))

    def testDrawCPermutation(self):
        self.assertCanBeDrawn(CPermutation((0, 2, 3, 1)))

    def testDrawSeries(self):
        self.assertCanBeDrawn(SeriesProduct(CircuitSymbol('a', 5), CircuitSymbol('b', 5)))

    def testDrawConcatenation(self):
        self.assertCanBeDrawn(Concatenation(CircuitSymbol('a', 5), CircuitSymbol('b', 5)))

    def testDrawIdentity(self):
        self.assertCanBeDrawn(cid(5))

    def testDrawFeedback(self):
        self.assertCanBeDrawn(Feedback(CircuitSymbol('M', 5), out_port=3, in_port=4))

    def testDrawNested(self):
        self.assertCanBeDrawn(
            SeriesProduct(CircuitSymbol('a', 2), Concatenation(CircuitSymbol('b', 1), CircuitSymbol('c', 1))))
        self.assertCanBeDrawn(
            Concatenation(CircuitSymbol('a', 2), SeriesProduct(CircuitSymbol('b', 1), CircuitSymbol('c', 1))))
        self.assertCanBeDrawn(
            Feedback(Concatenation(CircuitSymbol('a', 2), SeriesProduct(CircuitSymbol('b', 1), CircuitSymbol('c', 1))),
                out_port=2, in_port=0))

    def testDrawSLH(self):
        self.assertCanBeDrawn(SLH(identity_matrix(1), Matrix([[Create(hs=1)]]), Create(hs=1) * Destroy(hs=1)))


if __name__ == '__main__':
    unittest.main()

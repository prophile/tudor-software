try:
    import numpy
    class Matrix(object):
        def __init__(self, rows):
            self._impl = numpy.matrix(rows)

        def pseudo_inverse(self):
            return Matrix(numpy.linalg.pinv(self._impl))

        def __mul__(self, vector):
            lhs = numpy.matrix([[x] for x in vector])
            output = self._impl * lhs
            return tuple(float(value) for value in output)
except ImportError:
    # naive implementation without support for pseudoinverse
    class Matrix(object):
        def __init__(self, rows):
            self._rows = list(tuple(row) for row in rows)

        def pseudo_inverse(self):
            if (len(self._rows) == 3 and
                len(self._rows[0]) == 3):
                # direct inverse
                a, b, c = self._rows[0]
                d, e, f = self._rows[1]
                g, h, i = self._rows[2]
                det = a*e*i - a*f*h - b*d*i + b*f*g + c*d*h - c*e*g
                output = [[e*i - f*h, c*h - b*i, b*f - c*e],
                          [f*g - d*i, a*i - c*g, c*d - a*f],
                          [d*h - e*g, b*g - a*h, a*e - b*d]]
                for row in output:
                    for j in xrange(len(row)):
                        row[j] /= det
                return Matrix(output)
            raise NotImplementedError

        def __mul__(self, vector):
            return [sum(row[j] * vector[j] for j in xrange(len(vector)))
                                           for row in self._rows]


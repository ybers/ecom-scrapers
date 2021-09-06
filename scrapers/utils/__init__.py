from .xml_creator import OutputXML


class vendor_code_generator: # noqa
    """
    Sometimes companies do not have an article numbers.
    This class provides a feature of generating SKU numbers.

    :param prefix: A few letters in upper case that describe the name of the company.

    :param start: Company attribute 'last_generated_product_id' from database.
        Positive integer [0, 10e5)

    Usage:
    >>> c = vendor_code_generator('YB', 600)
    >>> next(c)
    ... 'YB000601'
    >>> c.last_generated_number
    ... 601
    """

    POW = 6
    MIN = 0
    MAX = 10 ** POW

    def __init__(self, /, prefix: str, start: int):
        if not self.MIN <= start < self.MAX:
            raise ValueError(
                'Start argument must be'
                ' greater or equal than {self.MIN}'
                ' and less than {self.MAX}.'.format(self=self)
            )
        self._prefix = prefix
        self._number = start

    @property
    def last_generated_number(self):
        return self._number

    def __next__(self):
        self._number += 1
        if self._number >= self.MAX:
            raise StopIteration
        return '{self._prefix}{self._number:0>{self.POW}}'.format(self=self)

    def __iter__(self):
        return self


__all__ = (
    OutputXML,
    vendor_code_generator,
)

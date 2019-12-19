"""Tests for path segments"""

from datetime import datetime

from bareasgi.basic_router.path_segment import PathSegment


def test_path_segment_literal():
    """Test a path segment literal"""
    seg = PathSegment("foo")
    assert seg.name == 'foo'
    assert not seg.is_variable
    assert seg.type is None
    assert seg.format is None
    is_match, variable_name, value = seg.match('foo')
    assert is_match
    assert variable_name is None
    assert value is None
    is_match, variable_name, value = seg.match('bar')
    assert not is_match
    assert variable_name is None
    assert value is None


def test_path_segment_variable():
    """Test a path segment"""
    seg = PathSegment("{foo}")
    assert seg.name == 'foo'
    assert seg.is_variable
    assert seg.type is 'str'
    assert seg.format is None
    is_match, variable_name, value = seg.match('bar')
    assert is_match
    assert variable_name == 'foo'
    assert value == 'bar'
    is_match, variable_name, value = seg.match('')
    assert is_match
    assert variable_name == 'foo'
    assert value == ''


def test_path_segment_variable_int():
    """Test a path segment"""
    seg = PathSegment("{foo:int}")
    assert seg.name == 'foo'
    assert seg.is_variable
    assert seg.type == 'int'
    assert seg.format is None
    is_match, variable_name, value = seg.match('42')
    assert is_match
    assert variable_name == 'foo'
    assert value == 42
    is_match, variable_name, value = seg.match('bar')
    assert not is_match
    assert variable_name is None
    assert value is None


def test_path_segment_variable_date():
    """Test a path segment"""
    seg = PathSegment("{foo:datetime:%Y-%m-%d}")
    assert seg.name == 'foo'
    assert seg.is_variable
    assert seg.type == 'datetime'
    assert seg.format == '%Y-%m-%d'
    is_match, variable_name, value = seg.match('1967-08-12')
    assert is_match
    assert variable_name == 'foo'
    assert value == datetime(1967, 8, 12)
    is_match, variable_name, value = seg.match('bar')
    assert not is_match
    assert variable_name is None
    assert value is None

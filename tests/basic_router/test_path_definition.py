"""Tests for path definitions"""

from datetime import datetime

from bareasgi.basic_router.path_definition import PathDefinition


def test_literal_paths():
    """Test for literal paths"""
    path_def = PathDefinition('/foo/bar/grum')
    is_match, matches = path_def.match('/foo/bar/grum')
    assert is_match
    assert matches == {}


def test_literal_path_with_trailing_slash():
    """Test for literal path with trailing slash"""
    path_def = PathDefinition('/foo/bar/grum/')

    is_match, matches = path_def.match('/foo/bar/grum/')
    assert is_match
    assert matches == {}


def test_variable_paths():
    """Test for path including a variable"""
    path_def = PathDefinition('/foo/{name}/grum')

    is_match, matches = path_def.match('/foo/bar/grum')
    assert is_match
    assert 'name' in matches
    assert matches['name'] == 'bar'


def test_variable_path_with_type():
    """Test for path with typed variable"""
    path_def = PathDefinition('/foo/{id:int}/grum')

    is_match, matches = path_def.match('/foo/123/grum')
    assert is_match
    assert matches is not None
    assert 'id' in matches
    assert matches['id'] == 123


def test_variable_path_with_type_and_format():
    """Test for path with typed variable and format"""
    path_def = PathDefinition('/foo/{date_of_birth:datetime:%Y-%m-%d}/grum')

    is_match, matches = path_def.match('/foo/2001-12-31/grum')
    assert is_match
    assert 'date_of_birth' in matches
    assert matches['date_of_birth'] == datetime(2001, 12, 31)


def test_path_type():
    """Test for path type"""
    path_def = PathDefinition('/ui/{rest:path}')

    is_match, matches = path_def.match('/ui/index.html')
    assert is_match
    assert 'rest' in matches
    assert matches['rest'] == 'index.html'

    is_match, matches = path_def.match('/ui/')
    assert is_match
    assert 'rest' in matches
    assert matches['rest'] == ''

    is_match, matches = path_def.match('/ui/folder/other.html')
    assert is_match
    assert 'rest' in matches
    assert matches['rest'] == 'folder/other.html'


def test_hashing():
    """Test that path definitions can be keys"""
    dct = {
        PathDefinition(path): path
        for path in ['/a/b', '/a/b/{c:int}']
    }
    for path_definition, path in dct.items():
        assert path_definition.path == path

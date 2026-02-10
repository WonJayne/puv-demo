from collections import defaultdict

import pytest

from openbus_light.plot._cmap import create_colormap


def test_dict_returned_without_default() -> None:
    """Test that create_colormap returns a regular dict when no default color is specified."""
    cmap = create_colormap(["a", "b"])
    assert isinstance(cmap, dict)
    assert not isinstance(cmap, defaultdict)
    with pytest.raises(KeyError):
        _ = cmap["missing"]


def test_defaultdict_returned_with_default_color() -> None:
    """Test that create_colormap returns a defaultdict when default color is specified."""
    cmap = create_colormap(["a", "b"], default_color="red")
    assert isinstance(cmap, defaultdict)
    assert cmap["missing"] == "red"
    assert cmap["a"] != "red"

import sys
import pytest
from mnamer.setting_store import SettingStore

pytestmark = pytest.mark.local


@pytest.fixture(autouse=True)
def reset_args():
    del sys.argv[:]
    sys.argv.append("mnamer")


# --- id extraction logic ---


@pytest.mark.parametrize(
    "path,field,expected",
    [
        (r"G:\Media\Show (2025) {tmdb-122781}\Season 01", "id_tmdb", "122781"),
        (r"G:\Media\Show (2025) {tvdb-12345}\Season 01", "id_tvdb", "12345"),
        (r"G:\Media\Show (2025) {tvmaze-999}\Season 01", "id_tvmaze", "999"),
        (r"G:\Media\Show (2025) {imdb-tt0123456}\Season 01", "id_imdb", "tt0123456"),
        (
            r"G:\Media\Show (2025) {imdb-0123456}\Season 01",
            "id_imdb",
            "tt0123456",
        ),  # tt prefix normalised
    ],
)
def test_id_parsed_from_folder(path, field, expected):
    sys.argv += ["--id-from-path", "--test", path]
    settings = SettingStore()
    settings.load()
    assert getattr(settings, field) == expected


def test_id_from_path_explicit_flag_wins():
    """Explicit --id-tmdb should not be overwritten by path."""
    sys.argv += [
        "--id-from-path",
        "--id-tmdb",
        "999",
        r"G:\Media\Show {tmdb-122781}\Season 01",
    ]
    settings = SettingStore()
    settings.load()
    assert settings.id_tmdb == "999"


def test_id_from_path_no_match():
    """No ID tag in path — fields stay None."""
    sys.argv += ["--id-from-path", "--test", r"G:\Media\Some Show\Season 01"]
    settings = SettingStore()
    settings.load()
    assert settings.id_tmdb is None
    assert settings.id_tvdb is None
    assert settings.id_imdb is None
    assert settings.id_tvmaze is None


def test_id_from_path_flag_off_by_default():
    """Without --id-from-path, IDs in path are ignored."""
    sys.argv += ["--test", r"G:\Media\Show {tmdb-122781}\Season 01"]
    settings = SettingStore()
    settings.load()
    assert settings.id_tmdb is None


def test_id_from_path_default_false():
    settings = SettingStore()
    assert settings.id_from_path is False


# --- flag registration ---


def test_id_from_path_flag_accepted():
    """--id-from-path must not raise 'invalid arguments'."""
    sys.argv += ["--id-from-path", "--test", r"G:\Media\Show {tmdb-1}\Season 01"]
    settings = SettingStore()
    settings.load()  # would raise MnamerException if flag unknown
    assert settings.id_from_path is True

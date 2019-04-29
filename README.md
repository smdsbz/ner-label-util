# ner-label-util
A simple TUI app labeling data for NER.

## Usage

```console
$ python3 app.py dump.json src.json
```

where `src.json` is ignored and optional, once `dump.json` is present as
a checkpoint.

### Operations

#### Program and Files

- `w`: Save to `dump.json`
- `q`: Quit (and save)

#### Movements

- `j` / `k`: Next / previous char
- `h` / `l`: Next / previous sentence

> Arrow keys are accepted.

#### Labeling

- `o`: Mark as out-of
- `b` / `I`: Mark as begining of an entity  
    This puts you into insert-mode, where you should give the tag a category
    name. Hit `<enter>` to commit.
- `i`: Mark as inside


## Configurations

- How many chars displayed on screen
    - See `margin` of `window.Window._describe_text_area()`. It controls how
        many chars to display before and after the current char.

    E.g. with `margin=3`, you get:

    ```text
    a  _
    b  _
    c  _
    d  _        // <- this is the current char
    e  _
    f  _
    g  _
    ```

    A large `margin` gives you better view of the context, but you must have
    that screen real estate.


## Requirements

- curses (pre-installed on *nix distributions of Python3)
- json (pre-installed)


from filterbox import load, save


def test_something_else(box_class, tmp_path):
    # create a file "myfile" in "mydir" in temp directory
    fn = tmp_path / "box.pkl"
    objs = [{"i": i} for i in range(10)]
    box = box_class(objs, "i")
    save(box, fn)
    box2 = load(fn)
    assert len(box2) == 10
    objs2 = list(box2)  # objs get cloned as well
    assert box2.find({"i": 3}) == [objs2[3]]
    assert box2.find({"i": [6]}) == [objs2[6]]
    assert box2.find({"i": {">": 8}}) == [objs2[9]]
    for obj in objs2:
        assert obj in box2

import pybook.t31 as t


def test_parse_csv():
    text = "id,name,score\n1,A,90\n2,B,ERROR\n3,A,80\n"
    errors, avgs = t.analyse_csv_text(text)
    assert "ERROR" in errors[0]
    assert avgs["A"] == 85.0

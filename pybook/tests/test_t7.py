import pybook.t7 as t


def test_non_singleton():
    dbInstance1 = t.DatabaseConnection("user1", "pass1")
    dbInstance2 = t.DatabaseConnection("user2", "pass2")
    assert dbInstance1.connect_str() == "user1:pass1"
    assert dbInstance2.connect_str() == "user2:pass2"
    assert dbInstance1 != dbInstance2


def test_singleton():
    dbInstance1 = t.DatabaseConnectionSingleton("user1", "pass1")
    dbInstance2 = t.DatabaseConnectionSingleton("user2", "pass2")
    assert dbInstance1.connect_str() == "user1:pass1"
    assert dbInstance2.connect_str() == "user1:pass1"
    assert dbInstance1 == dbInstance2

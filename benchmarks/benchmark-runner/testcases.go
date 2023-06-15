package main

type TestCase struct {
	Route    string
	Expected string
}

func ApiHello() *TestCase {
	return &TestCase{
		"/api/hello/Jeremy",
		`{"message":"Hello Jeremy!"}`,
	}
}

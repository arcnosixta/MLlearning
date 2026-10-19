package main
import "fmt"
type Named interface { Name() string }
type Student struct { name string }
func (s Student) Name() string { return s.name }
func label(n Named) string { return "Student: " + n.Name() }
func main() { fmt.Println(label(Student{name: "Aida"})) }

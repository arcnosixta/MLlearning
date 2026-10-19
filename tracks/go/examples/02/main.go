package main
import ("errors"; "fmt")
func divide(a, b int) (int, error) {
    if b == 0 { return 0, errors.New("division by zero") }
    return a / b, nil
}
func main() {
    value, err := divide(8, 2)
    if err != nil { fmt.Println(err); return }
    defer fmt.Println("done")
    fmt.Println(value)
}

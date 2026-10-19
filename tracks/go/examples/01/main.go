package main
import "fmt"
func main() {
    total := 0
    for i := 1; i <= 4; i++ { total += i }
    var ready bool
    fmt.Println(total, ready)
}

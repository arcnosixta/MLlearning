package main
import "fmt"
func sum(values []int) int { n:=0; for _,v:=range values { n+=v }; return n }
func main() {
    a:=[]int{2,4,6}; b:=make([]int,len(a)); copy(b,a); b[0]=9
    m:=map[string]int{"go":2}; _,ok:=m["java"]
    fmt.Println(sum(a),sum(b),ok)
}

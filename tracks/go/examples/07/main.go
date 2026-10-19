package main
import("fmt";"strings")
func main(){ cases:=[]struct{in,want string}{{" go ","go"},{"",""},{"  ",""}}; passed:=0
for _,c:=range cases { if strings.TrimSpace(c.in)==c.want {passed++} };fmt.Println(passed) }

package main
import("fmt";"strconv")
func port(s string)(int,error){ n,e:=strconv.Atoi(s);if e!=nil{return 0,e};if n<1||n>65535{return 0,fmt.Errorf("invalid port")};return n,nil }
func main(){n,e:=port("8080");fmt.Println(n,e==nil);_,e=port("70000");fmt.Println(e!=nil)}

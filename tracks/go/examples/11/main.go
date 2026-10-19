package main
import "fmt"
type Accounts struct{A,B int}
func transfer(a Accounts,n int)(Accounts,error){if n<=0||a.A<n{return a,fmt.Errorf("invalid transfer")};a.A-=n;a.B+=n;return a,nil}
func main(){before:=Accounts{10,2};after,e:=transfer(before,3);fmt.Println(after.A,after.B,e==nil);_,e=transfer(before,20);fmt.Println(before.A,before.B,e!=nil)}

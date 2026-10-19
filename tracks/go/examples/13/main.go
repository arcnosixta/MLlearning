package main
import "fmt"
type Store struct{values map[string]string}
func(s *Store)put(key,value string)error{if old,ok:=s.values[key];ok{if old!=value{return fmt.Errorf("conflict")};return nil};s.values[key]=value;return nil}
func main(){s:=Store{map[string]string{}};_ = s.put("k1","learn");_ = s.put("k1","learn");fmt.Println(len(s.values));fmt.Println(s.put("k1","other")!=nil)}

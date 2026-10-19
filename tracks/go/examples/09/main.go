package main
import("encoding/json";"fmt";"strings")
func main(){var c struct{Limit int `json:"limit"`};d:=json.NewDecoder(strings.NewReader(`{"limit":3}`));d.DisallowUnknownFields();if e:=d.Decode(&c);e!=nil{panic(e)};fmt.Println(c.Limit)}

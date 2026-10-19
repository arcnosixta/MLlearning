package main
import ("encoding/json"; "fmt"; "net/http"; "net/http/httptest")
func handler(w http.ResponseWriter,r *http.Request) {
    w.Header().Set("Content-Type","application/json")
    json.NewEncoder(w).Encode(struct{Ready bool `json:"ready"`}{true})
}
func main(){ r:=httptest.NewRequest("GET","/health",nil); w:=httptest.NewRecorder(); handler(w,r)
    fmt.Println(w.Code); fmt.Print(w.Body.String()) }

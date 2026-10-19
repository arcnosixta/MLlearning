package main
import("fmt";"net/http";"net/http/httptest";"strings")
func create(w http.ResponseWriter,r *http.Request){if r.Method!="POST"{w.WriteHeader(405);return};if strings.TrimSpace(r.URL.Query().Get("name"))==""{http.Error(w,"invalid_name",400);return};w.WriteHeader(201)}
func main(){for _,u:=range []string{"/tasks?name=Go","/tasks?name="}{w:=httptest.NewRecorder();create(w,httptest.NewRequest("POST",u,nil));fmt.Println(w.Code)}}

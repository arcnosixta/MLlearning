public class Main {
    interface Printable { String text(); }
    static class Report implements Printable {
        public String text() { return "Report ready"; }
    }
    static void print(Printable item) { System.out.println(item.text()); }
    public static void main(String[] args) { print(new Report()); }
}

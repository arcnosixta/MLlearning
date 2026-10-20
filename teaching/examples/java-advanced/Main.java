public class Main {
    interface MessageSource { String text(); }
    static class FixedSource implements MessageSource {
        public String text() { return "hello"; }
    }
    static void printMessage(MessageSource source) {
        System.out.println(source.text());
    }
    public static void main(String[] args) {
        printMessage(new FixedSource());
    }
}

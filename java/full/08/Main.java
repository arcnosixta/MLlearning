import java.util.ArrayList;
import java.util.List;
public class Main {
    enum State { NEW, PAID, CANCELLED }
    interface Formatter { String format(String value); }
    record Ticket(State state, List<String> items) {
        Ticket { items = List.copyOf(items); }
    }
    public static void main(String[] args) {
        List<String> source = new ArrayList<>(List.of("Java"));
        Ticket ticket = new Ticket(State.NEW, source);
        source.add("SQL");
        Formatter formatter = value -> "[" + value + "]";
        System.out.println(ticket.items().size());
        System.out.println(formatter.format(ticket.state().name()));
    }
}

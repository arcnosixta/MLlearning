import java.util.*;
public class Main {
    public static void main(String[] args) {
        List<String> original=new ArrayList<>(List.of("A"));
        List<String> view=Collections.unmodifiableList(original);
        List<String> snapshot=List.copyOf(original);
        original.add("B");
        System.out.println(view); System.out.println(snapshot);
    }
}

import java.util.*;
import java.util.stream.*;
public class Main {
    public static void main(String[] args) {
        Map<String,Long> counts=List.of("go","java","go").stream()
            .collect(Collectors.groupingBy(x->x,TreeMap::new,Collectors.counting()));
        String value=Optional.<String>empty().orElseGet(()->"missing");
        System.out.println(counts); System.out.println(value);
    }
}

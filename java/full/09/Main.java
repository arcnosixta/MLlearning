import java.lang.annotation.*;
import java.util.HashSet;
import java.util.List;
public class Main {
    @Retention(RetentionPolicy.RUNTIME)
    @Target(ElementType.TYPE)
    @interface Label { String value(); }
    @Label("catalog")
    record Key(String isbn) {}
    public static void main(String[] args) {
        var keys = new HashSet<>(List.of(new Key("A"), new Key("A")));
        System.out.println(keys.size());
        System.out.println(Key.class.getAnnotation(Label.class).value());
    }
}

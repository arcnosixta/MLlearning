import java.lang.annotation.*;
public class Main {
@Retention(RetentionPolicy.RUNTIME) @Target(ElementType.TYPE) @interface Topic{String value();}
@Topic("java") static class Lesson{}
public static void main(String[] args){Topic t=Lesson.class.getAnnotation(Topic.class);System.out.println(t==null?"missing":t.value());}}

public class Main {
interface Repository {String find();}
static class Memory implements Repository{public String find(){return "task";}}
static class Service {private final Repository repo;Service(Repository r){repo=r;}String title(){return repo.find().toUpperCase(java.util.Locale.ROOT);}}
public static void main(String[] args){System.out.println(new Service(new Memory()).title());}}

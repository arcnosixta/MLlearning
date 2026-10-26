"""Exercise the real chapter-20 SQL branch and transaction rollback in a private H2 database."""
import argparse
import os
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('driver', type=Path, help='H2 2.3.232 JDBC jar')
args = parser.parse_args()
assert args.driver.is_file(), args.driver
probe = '''import java.sql.*;
public class JdbcProbe {
    public static void main(String[] args) throws SQLException {
        String url="jdbc:h2:mem:rollback;DB_CLOSE_DELAY=-1";
        Main.database(url);
        try(Connection c=DriverManager.getConnection(url,"sa","")) {
            c.setAutoCommit(false);
            try(PreparedStatement insert=c.prepareStatement("INSERT INTO course_students(id,grade) VALUES (?,?)")) {
                insert.setInt(1,3);insert.setInt(2,75);insert.executeUpdate();
                insert.setInt(1,1);insert.executeUpdate();
                throw new AssertionError("duplicate key was accepted");
            } catch(SQLException expected) {c.rollback();}
            try(Statement query=c.createStatement();ResultSet r=query.executeQuery("SELECT COUNT(*) FROM course_students")) {
                r.next();if(r.getInt(1)!=2)throw new AssertionError("partial transaction survived");
            }
            try(PreparedStatement query=c.prepareStatement("SELECT grade FROM course_students WHERE id=?")) {
                query.setInt(1,999);
                try(ResultSet r=query.executeQuery()) {if(r.next())throw new AssertionError("missing row");}
            }
        }
        System.out.println("rollback=ok");
    }
}'''
with tempfile.TemporaryDirectory() as temporary:
    work = Path(temporary)
    (work / 'Main.java').write_text((ROOT / 'java/full/20/Main.java').read_text(encoding='utf-8'), encoding='utf-8')
    (work / 'JdbcProbe.java').write_text(probe, encoding='utf-8')
    compiled = subprocess.run(['javac', '--release', '17', '-encoding', 'UTF-8', 'Main.java', 'JdbcProbe.java'], cwd=work, capture_output=True, text=True, timeout=45)
    assert compiled.returncode == 0, compiled.stderr
    classpath = str(work) + os.pathsep + str(args.driver.resolve())
    result = subprocess.run(['java', '-cp', classpath, 'JdbcProbe'], cwd=work, capture_output=True, text=True, timeout=30)
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == 'students=2\naverage=90\nrollback=ok', result.stdout
print('PASS real JDBC connection, prepared statements, commit, rollback and absent-row handling')

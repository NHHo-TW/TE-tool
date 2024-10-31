=Title
    Author: NHHo
    Feature:
        T6391 histogram 疊圖工具
        先創建 IN 資料夾，將要分析的 hst 檔案放入並重新命名
        file 1: PA0401_XXXX.log -> V01_PA0401_XXXX.log
        file 2: PA0401_XXXX.log -> V02_PA0401_XXXX.log

        mode 0:
            多檔案疊圖，scale 採用第一個檔案，適用於多檔案要疊成單一圖表分析，且 scale 均一致
        mode 1:
            雙檔案疊圖，scale 採用第二個檔案，適用於更新程式有更改 scale 時
    Version:

    Notice:
        1. 要疊的測試項，版本前後測試項名稱要相同
        2. 輸出後的檔案可以透過 vba 來做快速繪圖 (VBA_histogram_tool)
=cut

my $mode = defined($ARGV[0]) ? $ARGV[0] : 0;
my $debug_on = defined($ARGV[1]) ? $ARGV[1] : 0;
my $in_dir = "IN";
my $out_dir = "OUT";
if (!-e $out_dir) {
    mkdir $our_dir, 0755;
)
my $tmp_dir = "TMP";
if (!-e $tmp_dir) {
    mkdir $tmp_dir, 0755;
)
my @files = <$in_dir/*.log>;
my @ver_arr = ();

foreach $file (@files) {
    open (f_source, "< $file");
    ($out_file = $file) =~ s/$in_dir/$tmp_dir/g;
    $file =~ /$in_dir\/(\w+)\-./;
    $ver_name = $1;
    push @ver_arr, $out_file;
    open (f_target, "+> $out_file");
    &initial();
    while ($line = <f_source>) {
        chomp $line;
        if ($st_flag == 1) {
            if ($line =~ /Count \/ Plot Character/) {
                print f_target "$test_id: ";
                print f_target "$title\n";
                print f_target "unit, $unit\n";
                $highlimit_str =~ s/TBD/$tmp_yvalue/g;
                $lowlimit_str  =~ s/TBD/$tmp_yvalue/g;
                print f_target "$xvalue_str\n";
                print f_target "$lowlimit_str\n";
                print f_target "$yvalue_str\n";
                print f_target "$highlimit_str\n";
                &initial();
                next;
            }
            @content = split ' ', $line;
            if (@content <5) {
                next;
            } elsif ($content[0] =~ /\=\=\>/) {
                $content[1] =~ /(-*\d+\.*\d*)(\D*)/;
                $xvalue = $1;
                $unit   = $2;
                if ($content[1] =~ /\E\+/) {
                    $times = substr($content[1], index($content[1], "E") + 2);
                    $times =~ s/\s+//g;
                    $unit = "";
                    $xvalue = $xvalue*(10**$times);
                }
                $line =~ /.*(\s+\d+\()\s*/;
                $yvalue = $1;
                $yvalue =~ s/\(//g;
                $yvalue =~ s/\s+//g;
                if ($yvalue > $tmp_yvalue) {
                    $tmp_yvalue = $yvalue;
                }
                if ($lowlimit eq "") {
                    $lowlimit = $xvalue;
                    $lowlimit_str = $lowlimit_str.","."TBD";
                    $highlimit_str = $highlimit_str.",".0;
                } else {
                    $highlimit = $xvalue;
                    $lowlimit_str = $lowlimit_str.",".0;
                    $highlimit_str = $highlimit_str.","."TBD";
                }
            } else {
                $content[0] =~ /(-*\d+\.*\d*)(\D*)/;
                $xvalue = $1;
                if ($content[0] =~ /E\+/) {
                    $times = substr($content[0], index($content[0], "E") + 2);
                    $times =~ s/\s+//g;
                    $xvalue = $xvalue*(10**$times);
                }
                $line =~ /.*)\s+\d+\()\s*/;
                $yvalue = $1;
                $yvalue =~ s/\(//g;
                $yvalue =~ s/\s+//g;
                if ($yvalue > $tmp_yvalue) {
                    $tmp_yvalue = $yvalue;
                }
                $lowlimit_str = $lowlimit_str.",".0;
                $highlimit_str = $highlimit_str.",".0;
            }
            $xvalue_str = $xvalue_str.",".$xvalue;
            $yvalue_str = $yvalue_str.",".$yvalue;
        } elsif ($st_flag == 0) {
            if ($line =~ /Title\:/) {
                ($title = $line) =~ s/\s*Title\:\s*//g;
            } elsif ($line =~ /Test ID\:/) {
                ($test_id = $line) =~ s/\s*Test ID\:\s*//g;
            }
        }
        #========== Histogram Start ==========#
        if ($line =~ /\s*Cell\s*\%\s*Histogram\s*Count\s*\(\s*Pass\s*\)\s*Sum\s*\%/) {
            $st_flag = 1;
        }
    }
    close (f_source);
    close (f_target);
}

&initial();

if ($mode == 0) {
    open (f_r1, "<$ver_arr[0]");
    open (f_target, "+> $out_dir/Histogram_Data.csv");
    while ($line_r1 = <f_r1>) {
        chomp $line_r1;
        if ($line_r1 =~ /\:/) {
            $st_flag = 1;
        }
        if ($st_flag == 1) {
            $id = $line_r1;
            print f_target "$line_r1\n";
            for (1..4) {
                $line_r1 = <f_r1>;
                print f_target "$line_r1";
            }
            for $i (1..@ver_arr-1) {
                open (f_r2, "< $ver_arr[$i]");
                while ($line_r2 = <f_r2>) {
                    chomp $line_r2;
                    if ($line_r2 eq $id) {
                        for (1..4) {
                            $line_r2 = <f_r2>;
                        }
                        print f_target "$line_r2";
                        $write_flag = 1;
                        last;
                    }
                }
                close (f_r2);
            }
            $line_r1 = <f_r1>;
            print f_target "$line_r1\n";
            &initial();
        }
    }
    close (f_target);
    close (f_r1);
}

#========== Remove TMP dir ==========#
if ($debug_on == 0) {
    unlink glob "$tmp_dir/*";
    rmdir $tmp_dir;
} else {
    system "PAUSE";
}

#========== Reset global value ==========#
sub initial() {
    $st_flag = 0;
    $lowlimit = "";
    $highlimit = "";
    $unit = "";
    $xvalue = "";
    $yvalue = "";
    $xvalue_str = "X_Coor";
    $yvalue_str = $ver_name;
    $lowlimit_str = "Llimit";
    $highlimit_str = "Hlimit";
    $tmp_yvalue = 0;
    $write_flag = 0;
}

/* 1. Import dataset */
libname sas "../personal_projects/data";

proc import
    datafile="../data/Dataset_spine.csv"
    out=sas.spine
    dbms=csv
    replace;
    guessingrows=max;
run;

/* 2. Rename features */
data sas.spine;
    set sas.spine;

    rename
        'pelvic incidence'n = pelvic_incidence
        ' pelvic tilt'n = pelvic_tilt
        ' lumbar lordosis angle'n = lumbar_lordosis
        ' sacral slope'n = sacral_slope
        ' pelvic radius'n = pelvic_radius
        ' grade of spondylolisthesis'n = spondylolisthesis_grade;
run;

/* 3. Binary classification target */
data sas.spine_binary;
    set sas.spine;
    length binary_target 8;
    select (upcase(strip(class_att)));
        when ("ABNORMAL", "YES", "1")
            binary_target = 1;
        when ("NORMAL", "NO", "0")
            binary_target = 0;
        otherwise binary_target = .;
    end;
    if missing(binary_target) then delete;
run;

/* Note: Eliminated pelvic radius due to highly correlated */
/* 4. Define predictors */
%let feature_input =
    pelvic_incidence
    pelvic_tilt
    lumbar_lordosis
    spondylolisthesis_grade;

%let target_input = binary_target;

/* 7. Logistic Regression */
ods graphics on;

proc logistic data=sas.spine_binary
              plots(only)=roc;
    model &target_input.(event='1')
        = &feature_input.
        / clodds=wald;
    roc;
run;

ods graphics off;

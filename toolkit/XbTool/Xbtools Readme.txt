Required Arguments:
  -g, --game <game>  Game the input data is from (xb1 | xbx | xb2)
  -t, --task <task>  Task to perform

Other Options:
  -a, --archive <arh> <ard>   Input Xenoblade 2 archive file
  -b, --bdat <path>           Directory to load BDAT files from
  -i <path>                   Input file or directory
  -o <path>                   Output file or directory
  -f, --filter <pattern>      Search pattern to use when reading a directory
                              Usable whenever inputting a directory

Tasks:
  ExtractArchive - Extracts Xenoblade 2's file archive
    ExtractArchive -a <archive> -o <output_path>

  DecryptBdat - Decrypts a BDAT file or directory
    DecryptBdat -i <input_file> [-o <output_file>]
    DecryptBdat -i <input_dir>

  BdatCodeGen - Generates code for deserializing BDAT files
    BdatCodeGen (-a <archive> | -b <bdat_dir>) -o <output_dir>

  Bdat2Html - Generates HTML tables from BDAT files
    Bdat2Html (-a <archive> | -b <bdat_dir>) -o <output_dir>

  Bdat2Json - Generates JSON files from BDAT files
    Bdat2Json (-a <archive> | -b <bdat_dir>) -o <output_dir>

  GenerateData - Generates various data from BDAT files
    GenerateData (-a <archive> | -b <bdat_dir>) -o <output_dir>

  DescrambleScript - Descrambles a .sb script file or directory
    DescrambleScript -i <input_file> [-o <output_file>]
    DescrambleScript -i <input_dir>

  ExtractWilay - Extracts textures from .wilay files
                 When reading from an archive, -i specifies the
                 directory in the archive to search e.g. /menu/image
    ExtractWilay -i <input_path> -o <output_dir>
    ExtractWilay -a <archive> [-i <input_path>] -o <output_dir>

  CreateBlade - Runs the Xenoblade 2 common blade generator
    CreateBlade (-a <archive> | -b <bdat_input_dir>)

  ReadSave - XB2 save file reading example
             Outputs common blade information
    ReadSave (-a <archive> | -b <bdat_input_dir>) -i <save_file> -o <out_text_file>
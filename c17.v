module bench\c17 ( 
    \1 , 2, 3, 6, 7,
    22, 23  );
  input  \1 , 2, 3, 6, 7;
  output 22, 23;
  wire n7, n8, n9, n11;
  NAND2_X1 g0(.A1(3), .A2(\1 ), .ZN(n7));
  NAND2_X1 g1(.A1(6), .A2(3), .ZN(n8));
  NAND2_X1 g2(.A1(n8), .A2(2), .ZN(n9));
  NAND2_X1 g3(.A1(n9), .A2(n7), .ZN(22));
  NAND2_X1 g4(.A1(n8), .A2(7), .ZN(n11));
  NAND2_X1 g5(.A1(n11), .A2(n9), .ZN(23));
endmodule
# encoding: utf-8
# Copyright (C) 2015 John Törnblom

from utils import RSLTestCase
from utils import evaluate


from rsl.runtime import RuntimeException


class TestConstLiterals(RSLTestCase):

    @evaluate
    def testUpperCase(self, rc):
        '''
        .assign x = "hello"
        .exit "$U{x}"
        '''
        self.assertEqual("HELLO", rc)

    @evaluate
    def testLowerCase(self, rc):
        '''
        .assign x = "HELlo"
        .exit "$L{x}"
        '''
        self.assertEqual("hello", rc)

    @evaluate
    def testCapitalize(self, rc):
        '''
        .assign x = "heLLO"
        .exit "$C{x}"
        '''
        self.assertEqual("Hello", rc)

    @evaluate
    def testEscapeSingleQuote(self, rc):
        '''
        .assign x = "'"
        .exit "$t2tick{x}"
        '''
        self.assertEqual("''", rc)
        
    @evaluate
    def testUnderscore(self, rc):
        '''
        .assign x = "hello world"
        .exit "$_{x}"
        '''
        self.assertEqual("hello_world", rc)

    @evaluate
    def testcOrba(self, rc):
        '''
        .assign x = "HelLO woRLd"
        .exit "$o{x}"
        '''
        self.assertEqual("helloWorld", rc)

    @evaluate
    def testcOrbaWithUnderline(self, rc):
        '''
        .assign x = "Hello_world!"
        .exit "$o{x}"
        '''
        self.assertEqual("helloWorld", rc)
        
    @evaluate
    def testcOrbaWithEmptyString(self, rc):
        '''
        .assign x = ""
        .exit "$o{x}"
        '''
        self.assertEqual("", rc)
        
    @evaluate
    def testExampleU(self, rc):
        '''
        .assign x = "Example Text"
        .exit "$u{x}"
        '''
        self.assertEqual("EXAMPLE TEXT", rc)
        
    @evaluate
    def testExampleU_(self, rc):
        '''
        .assign x = "Example Text"
        .exit "$u_{x}"
        '''
        self.assertEqual("EXAMPLE_TEXT", rc)

    @evaluate
    def testExampleUR(self, rc):
        '''
        .assign x = "Example Text"
        .exit "$ur{x}"
        '''
        self.assertEqual("EXAMPLETEXT", rc)

    @evaluate
    def testExampleC(self, rc):
        '''
        .assign x = "ExamplE TExt"
        .exit "$c{x}"
        '''
        self.assertEqual("Example Text", rc)
        
    @evaluate
    def testExampleC_(self, rc):
        '''
        .assign x = "ExamplE TExt"
        .exit "$c_{x}"
        '''
        self.assertEqual("Example_Text", rc)
        
    @evaluate
    def testExampleCR(self, rc):
        '''
        .assign x = "ExamplE TExt"
        .exit "$cr{x}"
        '''
        self.assertEqual("ExampleText", rc)
        
    @evaluate
    def testExampleL(self, rc):
        '''
        .assign x = "ExamplE TExt"
        .exit "$l{x}"
        '''
        self.assertEqual("example text", rc)
        
    @evaluate
    def testExampleL_(self, rc):
        '''
        .assign x = "ExamplE TExt"
        .exit "$l_{x}"
        '''
        self.assertEqual("example_text", rc)
        
    @evaluate
    def testExampleLR(self, rc):
        '''
        .assign x = "ExamplE TExt"
        .exit "$lr{x}"
        '''
        self.assertEqual("exampletext", rc)
        
    @evaluate
    def testExampleO(self, rc):
        '''
        .assign x = "ExamplE@34 TExt"
        .exit "$o{x}"
        '''
        self.assertEqual("example34Text", rc)
        
    @evaluate
    def testChain(self, rc):
        '''
        .function assertEquals
          .param string actual
          .param string expected
          .param integer test_num
          .if ( actual != expected )
            .exit "chain test ${test_num} failed, expected = ${expected} actual = ${actual}"
          .end if
        .end function
        
        .function tcf_kl_test
          .param string test_string
          .param string expected
          .param integer test_num
          .invoke assertEquals("$tcf_kl{test_string}", expected, test_num)
        .end function
        
        .function tcb_kl_test
          .param string test_string
          .param string expected
          .param integer test_num
          .invoke assertEquals("$tcb_kl{test_string}", expected, test_num)
        .end function
        
        .function tcf_rel_test
          .param string test_string
          .param string expected
          .param integer test_num
          .invoke assertEquals("$tcf_rel{test_string}", expected, test_num)
        .end function
        
        .function tcb_rel_test
          .param string test_string
          .param string expected
          .param integer test_num
          .invoke assertEquals("$tcb_rel{test_string}", expected, test_num)
        .end function
        
        .function tcf_phrase_test
          .param string test_string
          .param string expected
          .param integer test_num
          .invoke assertEquals("$tcf_phrase{test_string}", expected, test_num)
        .end function
        
        .function tcb_phrase_test
          .param string test_string
          .param string expected
          .param integer test_num
          .invoke assertEquals("$tcb_phrase{test_string}", expected, test_num)
        .end function
        
        .function tcf_rest_test
          .param string test_string
          .param string expected
          .param integer test_num
          .invoke assertEquals("$tcf_rest{test_string}", expected, test_num)
        .end function
        
        .function tcb_rest_test
          .param string test_string
          .param string expected
          .param integer test_num
          .invoke assertEquals("$tcb_rest{test_string}", expected, test_num)
        .end function

        .assign test_string0 = "->A[R1]->B[R2]"
        .assign test_string1 = "->C[R3]->D[R4.'b1 phrase']"
        .assign test_string2 = "->E[R5.'a2 phrase']->F[R6]"
        .assign test_string3 = "->G[R7.'a3 phrase']->H[R8.'b3 phrase']"
        .assign test_string4 = ""
        
        .invoke tcf_kl_test(test_string0, "A", 1)
        .invoke tcf_kl_test(test_string1, "C", 2)
        .invoke tcf_kl_test(test_string2, "E", 3)
        .invoke tcf_kl_test(test_string3, "G", 4)
        .invoke tcb_kl_test(test_string0, "B", 5)
        .invoke tcb_kl_test(test_string1, "D", 6)
        .invoke tcb_kl_test(test_string2, "F", 7)
        .invoke tcb_kl_test(test_string3, "H", 8)
        
        .invoke tcf_rel_test(test_string0, "1", 9)
        .invoke tcf_rel_test(test_string1, "3", 10)
        .invoke tcf_rel_test(test_string2, "5", 11)
        .invoke tcf_rel_test(test_string3, "7", 12)
        .invoke tcb_rel_test(test_string0, "2", 13)
        .invoke tcb_rel_test(test_string1, "4", 14)
        .invoke tcb_rel_test(test_string2, "6", 15)
        .invoke tcb_rel_test(test_string3, "8", 16)
        
        .invoke tcf_rest_test(test_string0, "->B[R2]", 17)
        .invoke tcf_rest_test(test_string1, "->D[R4.'b1 phrase']", 18)
        .invoke tcf_rest_test(test_string2, "->F[R6]", 19)
        .invoke tcf_rest_test(test_string3, "->H[R8.'b3 phrase']", 20)
        .invoke tcb_rest_test(test_string0, "->A[R1]", 21)
        .invoke tcb_rest_test(test_string1, "->C[R3]", 22)
        .invoke tcb_rest_test(test_string2, "->E[R5.'a2 phrase']", 23)
        .invoke tcb_rest_test(test_string3, "->G[R7.'a3 phrase']", 24)
        
        .invoke tcf_phrase_test(test_string0, "", 25)
        .invoke tcf_phrase_test(test_string1, "", 26)
        .invoke tcf_phrase_test(test_string2, "a2 phrase", 27)
        .invoke tcf_phrase_test(test_string3, "a3 phrase", 28)
        .invoke tcb_phrase_test(test_string0, "", 29)
        .invoke tcb_phrase_test(test_string1, "b1 phrase", 30)
        .invoke tcb_phrase_test(test_string2, "", 31)
        .invoke tcb_phrase_test(test_string3, "b3 phrase", 32)
        

        .invoke tcf_kl_test(test_string4, "", 33)
        .invoke tcb_kl_test(test_string4, "", 34)

        .exit 0
        '''
        if rc:
            self.fail(rc)

    
    @evaluate
    def testEmptyTSTRSEP_(self, rc):
        '''
        .assign x = ""
        .exit "$tstrsep_{x}"
        '''
        self.assertEqual("",rc)

    @evaluate
    def testTSTRSEP_(self, rc):
        '''
        .assign x = "Hej_Hopp"
        .exit "$tstrsep_{x}"
        '''
        self.assertEqual("Hej",rc)

    @evaluate
    def testNo_TSTRSEP_(self, rc):
        '''
        .assign x = "No"
        .exit "$tstrsep_{x}"
        '''
        self.assertEqual("No",rc)

    @evaluate
    def testT_STRSEP(self, rc):
        '''
        .assign x = "Hej_Hopp"
        .exit "$t_strsep{x}"
        '''
        self.assertEqual("Hopp",rc)

    @evaluate
    def testNo_T_STRSEP(self, rc):
        '''
        .assign x = "No"
        .exit "$t_strsep{x}"
        '''
        self.assertEqual("",rc)

    @evaluate
    def testExampleTXMLCLEAN(self, rc):
        '''
        .assign x = "ExamplETExt"
        .exit "$txmlclean{x}"
        '''
        self.assertEqual("ExamplETExt", rc)

    @evaluate
    def testXMLTXMLCLEAN(self, rc):
        '''
        .assign x = "&<>"
        .exit "$txmlclean{x}"
        '''
        self.assertEqual("&amp;&lt;&gt;", rc)

    @evaluate
    def testTXMLQUOT(self, rc):
        '''
        .assign x = "B'"
        .assign y = "C"
        .exit "$txmlquot{x} $txmlquot{y}"
        '''
        self.assertEqual(""""B'" 'C'""",rc)

    @evaluate
    def testTXMLNAME(self, rc):
        '''
        .assign x1 = "B"
        .assign x2 = "C.9"
        .assign x3 = "D_9"
        .assign x4 = "E-9"
        .assign x5 = ".G"
        .assign x6 = "-H"
        .assign x7 = "_I"
        .exit "$txmlname{x1} $txmlname{x2} $txmlname{x3} $txmlname{x4} $txmlname{x5} $txmlname{x6} $txmlname{x7}"
        '''
        self.assertEqual("B C.9 D_9 E-9 _G _H _I",rc)

    @evaluate
    def testTU2D(self, rc):
        '''
        .assign x = "-_"
        .exit "$tu2d{x}"
        '''
        self.assertEqual("--", rc)

    @evaluate
    def testTD2U(self, rc):
        '''
        .assign x = "-_"
        .exit "$td2u{x}"
        '''
        self.assertEqual("__", rc)

    @evaluate
    def testInvalidFormat(self,rc):
        '''
        .assign x = "-_"
        .exit "$tsomethinginvalid{x}"
        '''
        self.assertIsInstance(rc, RuntimeException)


    @evaluate
    def testTInBody(self,rc):
        '''
        .function f
          .param string s
Hej $t{s}
        .end function
        .invoke rc = f("Hej!")
        .exit "${rc.body}"
        '''
        self.assertEqual("Hej Hej!\n", rc)

    @evaluate
    def testDollarDollarInLiteral(self,rc):
        '''
        .exit "$${baff}"
        '''
        self.assertEqual("${baff}", rc)

    @evaluate
    def testSubstInSubst(self, rc):
        '''
        .assign a = "b"
        .assign b = "Hej"
        .exit "${${a}}"
        '''
        self.assertEqual("b", rc)

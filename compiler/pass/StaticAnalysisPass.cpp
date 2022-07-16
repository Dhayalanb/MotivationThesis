#include "llvm/ADT/DenseSet.h"
#include "llvm/ADT/SmallPtrSet.h"
#include "llvm/ADT/SmallSet.h"
#include "llvm/ADT/SmallVector.h"
#include "llvm/ADT/Statistic.h"
#include "llvm/Analysis/ValueTracking.h"
#include "llvm/IR/Argument.h"
#include "llvm/IR/Constant.h"
#include "llvm/IR/Constants.h"
#include "llvm/IR/DebugInfo.h"
#include "llvm/IR/Function.h"
#include "llvm/IR/IRBuilder.h"
#include "llvm/IR/Instructions.h"
#include "llvm/IR/LegacyPassManager.h"
#include "llvm/IR/MDBuilder.h"
#include "llvm/IR/Module.h"
#include "llvm/Pass.h"
#include "llvm/Support/Casting.h"
#include "llvm/Support/Debug.h"
#include "llvm/Support/raw_ostream.h"
#include "llvm/Transforms/IPO/PassManagerBuilder.h"
#include "llvm/Transforms/Utils/BasicBlockUtils.h"
#include <llvm/IR/BasicBlock.h>
#include <llvm/IR/User.h>
#include <llvm/Analysis/CFG.h>

#include <algorithm>
#include <fstream>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <map>


#include "./debug.h"
#include "./defs.h"
#include "./abilist.h"

#define DEBUG_TYPE "static-metrics"

using namespace llvm;

const char *CompareFuncCat = "cmpfn";

static cl::list<std::string> ClExploitListFiles(
    "angora-exploitation-list",
    cl::desc("file listing functions and instructions to exploit"), cl::Hidden);

// hash file name and file size
u32 hashName(std::string str)
{
  std::ifstream in(str, std::ifstream::ate | std::ifstream::binary);
  u32 fsize = in.tellg();
  u32 hash = 5381 + fsize * 223;
  for (auto c : str)
    hash = ((hash << 5) + hash) + (unsigned char)c; /* hash * 33 + c */
  return hash;
}

STATISTIC(UnhandledConditions, "Number of unhandled conditions");

namespace
{
  class StaticMetrics : public ModulePass
  {

    struct Metrics
    {
      size_t CmpSize = 0;
      size_t NumCases = 0;
      bool ComparesConstant = false;
      bool ComparesPointer = false;
      bool IsEquality = false;
      bool IsConstant = false;
    };

    std::string ModName;
    std::error_code error;
    std::string str;
    int bbCount;
    u32 ModId;
    u32 CidCounter;
    bool is_bc;
    u32 BBID = 1;
    // Const Variables
    DenseSet<u32> UniqCidSet;
    // If there is a compare in the basic block then the basic block gets this hashID too
    std::map<BasicBlock*, int> basicBlockMap;
    std::map<BasicBlock*, u32> basicBlockMapUniqID;     

    // Configurations
    bool gen_id_random;
    bool output_cond_loc;

    // Meta
    unsigned NoSanMetaId;

    AngoraABIList ExploitList;

    std::unique_ptr<std::ofstream> Output;

    void getComplexity(Function const &F, unsigned &Cyclomatic, unsigned &Oviedo);
    Value const *handleBranchCondition(Value const *V, Metrics &M);
    void computeBackSlice(Instruction const *I,
                          SmallVectorImpl<User const *> &Chain);
    u32 getInstructionId(Instruction *Inst);
    void initVariables(Module &M);
    bool shouldVisitCallInstruction(Instruction *Inst);
    bool writeFunctionCFGtofile(Function &F);
    std::string  bbname(BasicBlock &B);

  public:
    static char ID;

    StaticMetrics() : ModulePass(ID) {
      bbCount = 0;
    }

    void getAnalysisUsage(AnalysisUsage &AU) const override
    {
      AU.setPreservesAll();
    }

    bool runOnModule(Module &M) override;
    void print(raw_ostream &O, Module const *) const override;
  };
} // namespace

char StaticMetrics::ID = 0;

u32 StaticMetrics::getInstructionId(Instruction *Inst) 
{
  u32 h = 0;
  if (is_bc)
  {
    h = ++CidCounter;
  }
  else
  {
    DILocation *Loc = Inst->getDebugLoc();
    if (Loc)
    {
      u32 Line = Loc->getLine();
      u32 Col = Loc->getColumn();
      h = (Col * 33 + Line) * 33 + ModId;
    }
    else
    {
      //error
      errs() << "Unknown location!\n";
      errs() << "[INS] " << *Inst << "\n";
      throw "Unknown location!";
    }

    while (UniqCidSet.count(h) > 0)
    {
      h = h * 3 + 1;
    }
    UniqCidSet.insert(h);
  }

  if (output_cond_loc)
  {
    errs() << "[ID] " << h << "\n";
    errs() << "[INS] " << *Inst << "\n";
    if (DILocation *Loc = Inst->getDebugLoc())
    {
      errs() << "[LOC] " << cast<DIScope>(Loc->getScope())->getFilename()
             << ", Ln " << Loc->getLine() << ", Col " << Loc->getColumn()
             << "\n";
    }
  }

  return h;
}

void StaticMetrics::initVariables(Module &M)
{
  // To ensure different version binaries have the same id
  ModName = M.getModuleIdentifier();
  if (ModName.size() == 0)
    FATAL("No ModName!\n");
  ModId = hashName(ModName);
  errs() << "ModName: " << ModName << " -- " << ModId << "\n";
  is_bc = 0 == ModName.compare(ModName.length() - 3, 3, ".bc");
  if (is_bc)
  {
    errs() << "Input is LLVM bitcode\n";
  }

  // set seed
  srandom(ModId);
  CidCounter = 0;
  LLVMContext &C = M.getContext();
  NoSanMetaId = C.getMDKindID("nosanitize");

  output_cond_loc = !!getenv(OUTPUT_COND_LOC_VAR);

  if (output_cond_loc)
  {
    errs() << "Output cond log\n";
  }

  std::vector<std::string> AllExploitListFiles;
  AllExploitListFiles.insert(AllExploitListFiles.end(),
                             ClExploitListFiles.begin(),
                             ClExploitListFiles.end());
  ExploitList.set(SpecialCaseList::createOrDie(AllExploitListFiles));
};

std::string StaticMetrics::bbname(BasicBlock &B){
  std::string name =std::to_string(basicBlockMap[&B]); 
  if (basicBlockMapUniqID.find(&B)== basicBlockMapUniqID.end()) return name;
  name = std::to_string(basicBlockMapUniqID[&B]);
  return name;
}



bool StaticMetrics::writeFunctionCFGtofile(Function &F)
{
  /*
   This is where we open the file to store the cfg for the function
  */
  char const *output_location = getenv("OUTPUT_STATIC_ANALYSIS_LOC_VAR");
  std::string CFG_dir = std::string(output_location);
  raw_string_ostream rso(str);

  std::string name = std::string(F.getName());
  name = CFG_dir+"/analysis/"+name;
  std::ofstream file_analysis;
  file_analysis.open (name, std::ofstream::out);

  name = name + ".dot";
  std::ofstream file;
  file.open (name, std::ofstream::out);

  errs() <<"\nName of the file is " << name  << " and the name of the function is "<< std::string(F.getName())<< "\n";
  enum sys::fs::OpenFlags F_None;
	
  
  // if(file_analysis)
  // {
  //   errs() <<"\n There is an erro trying to open the file"<< name <<"\n";
  // }

  //file << "digraph \"CFG for'" + F.getName() + "\' function\" {\n";
  file << "digraph G{\n";
  for (Function::iterator B_iter = F.begin(); B_iter != F.end(); ++B_iter){
				BasicBlock* curBB = &*B_iter;
				std::string name = curBB->getName().str();
				int fromCountNum;
				int toCountNum;
				if (basicBlockMap.find(curBB) != basicBlockMap.end())
				{
					fromCountNum = basicBlockMap[curBB];
				}
				else
				{
					fromCountNum = bbCount;
					basicBlockMap[curBB] = bbCount++;
				}

        
        //file << "\t" << bbname(*curBB) << " [shape=record, label=\"{";
				//file << "" << bbname(*curBB) << ":\\l\\l";
				for (BasicBlock::iterator I_iter = curBB->begin(); I_iter != curBB->end(); ++I_iter) {
					//printInstruction(&*I_iter,  os);
          Instruction* inst = &*I_iter;
          if (inst->getMetadata(NoSanMetaId)){
          continue;}
         
					//file << *I_iter << "\\l\n";
				}
				//file << "}\"];\n";
				for (BasicBlock *SuccBB : successors(curBB)){
					if (basicBlockMap.find(SuccBB) != basicBlockMap.end())
					{
						toCountNum = basicBlockMap[SuccBB];
					}
					else
					{
						toCountNum = bbCount;
						basicBlockMap[SuccBB] = bbCount++;
					}

					file << "\t" <<"BB"<<bbname(*curBB)<< "->"
						<<"BB"<< bbname(*SuccBB) << ";\n";

          file_analysis<<bbname(*curBB)<< ","
						<<bbname(*SuccBB) << "\n";

          // if (basicBlockMapUniqID.find(curBB)!= basicBlockMapUniqID.end() && basicBlockMapUniqID.find(SuccBB)!= basicBlockMapUniqID.end()){
          //   *adjfile  << bbname(*curBB)<< ","
					// 	<< bbname(*SuccBB) << "\n";
          //   }
				}
			}
			file << "}\n";
			file.close();
			return true;
		}



bool StaticMetrics::shouldVisitCallInstruction(Instruction *Inst)
{

  CallInst *Caller = dyn_cast<CallInst>(Inst);
  Function *Callee = Caller->getCalledFunction();

  if (!Callee || Callee->isIntrinsic() || isa<InlineAsm>(Caller->getCalledValue()))
  {
    return false;
  }

  // remove inserted "unfold" functions
  if (!Callee->getName().compare(StringRef("__unfold_branch_fn")))
  {
    if (Caller->use_empty())
    {
      return false;
    }
  }
  if (!ExploitList.isIn(*Inst, CompareFuncCat))
  {
    return false;
  }
  return true;
};

// The main runOnModule

bool StaticMetrics::runOnModule(Module &M)
{
  errs() << "Running static pass\n";
  initVariables(M);

  raw_string_ostream rso(str);
  enum sys::fs::OpenFlags F_None;
  enum sys::fs::OpenFlags F_Append;
  // std::ofstream adjfile;
  // adjfile.open ("adj.txt", std::ofstream::out | std::ofstream::app);

  // This code is for generating the output file
  if (!Output)
  {
    char const *output_location = getenv("OUTPUT_STATIC_ANALYSIS_LOC_VAR");
    if (!output_location) {
      output_location = "./static_analysis_results.";
    }
      errs() << "Output file name is "<< output_location << "\n";


    Output =         make_unique<std::ofstream>(std::string(output_location)+"/Static/static_analysis_results." + std::to_string(ModId) + std::string(".out"), std::ios::out);
    assert(Output->good() && "Stream to output file is not feeling good...");
    *Output << "BasicBlock,Condition,Cyclomatic,Oviedo,ChainSize,CompareSize,"
               "ComparesConstant,ComparesPointer,IsEquality,IsConstant,Cases\n";
  }

  SmallVector<User const *, 32> Chain;
  // raw_fd_ostream fileID("getInstruction.txt", error, F_None);
  for (auto &F : M) // for every function in the module
  {
    if (F.isDeclaration() || F.getName().startswith(StringRef("asan.module")))
      continue;

    LLVM_DEBUG(dbgs() << "Function: " << F.getName() << '\n');

    unsigned CyclomaticNumber = 0;
    unsigned OviedoComplexity = 0;
    getComplexity(F, CyclomaticNumber, OviedoComplexity);
    std::vector<BasicBlock *> bb_list;
    for (auto bb = F.begin(); bb != F.end(); bb++)
      bb_list.push_back(&(*bb));
    for (auto bi = bb_list.begin(); bi != bb_list.end(); bi++)
    {
      BasicBlock *BB = *bi;
      BBID++;
      std::vector<Instruction *> inst_list;

      for (auto inst = BB->begin(); inst != BB->end(); inst++) // iterates through all the instructions in the basic blocks and pushes them in the isntruction vector
      {
        Instruction *Inst = &(*inst);
        inst_list.push_back(Inst);
      }

      for (auto inst = inst_list.begin(); inst != inst_list.end(); inst++)
      {
        auto I = *inst;
        Metrics M;
        if (I->getMetadata(NoSanMetaId)){
          continue;}
        if (isa<CallInst>(I) && !shouldVisitCallInstruction(I)) // if its a call instruction
        {
          continue;
        }
        if (auto *CmpI = dyn_cast<CmpInst>(I)) // if the instruction is an compare instruction
        {
          Instruction *InsertPoint = CmpI->getNextNode();
          if (!InsertPoint || isa<ConstantInt>(CmpI))
            continue;
          M.CmpSize = CmpI->getOperand(0)->getType()->getScalarSizeInBits();
          M.ComparesPointer = CmpI->getOperand(0)->getType()->isPointerTy();
          M.ComparesConstant = isa<Constant>(CmpI->getOperand(0)) ||
                               isa<Constant>(CmpI->getOperand(1));

          auto P = CmpI->getPredicate();
          M.IsEquality = P == CmpInst::Predicate::ICMP_EQ ||
                         P == CmpInst::Predicate::FCMP_OEQ ||
                         P == CmpInst::Predicate::FCMP_UEQ;
        }
        else if (isa<CallInst>(I) || isa<InvokeInst>(I)) //if the instruction is a callinstr or invokeinstr
        {
          if (isa<InvokeInst>(I))
          {
            InvokeInst *Caller = dyn_cast<InvokeInst>(I);
            Function *Callee = Caller->getCalledFunction();

            if (!Callee || Callee->isIntrinsic() ||
                isa<InlineAsm>(Caller->getCalledValue()))
            {
              continue;
            }
          }
          M.CmpSize = 64;
          M.ComparesPointer = false;
          M.ComparesConstant = false;
          M.IsEquality = true;
        }
        else if (auto *Branch = dyn_cast<BranchInst>(I)) // if the instruction is a branch instruction
        {
          if (!Branch->isConditional()) //if the branch is not conditional
            continue;

          auto *Condition = handleBranchCondition(Branch->getCondition(), M);
          if (!Condition)
          {
            continue;
          }

          M.NumCases = Branch->getNumSuccessors();
          LLVM_DEBUG(dbgs() << "Branch " << BBID << ":\n"
                            << *Condition << '\n');
        }
        else if (auto *Switch = dyn_cast<SwitchInst>(I)) // if the instruction is a switch instruction
        {
          M.CmpSize = Switch->getType()->getScalarSizeInBits();
          M.NumCases = Switch->getNumCases();
          M.ComparesConstant = true;
          M.ComparesPointer = false;
          M.IsEquality = true;
          LLVM_DEBUG(dbgs() << "Switch " << BBID <<  ":\n"
                            << *Switch << '\n');
        }
        else
        {
          continue; //if its any other instruction just skip
        }
        try
        {
          //basicBlockMapUniqID;

          u32 getInstructionIdreturn = getInstructionId(I);
          if(basicBlockMapUniqID.find(*bi)== basicBlockMapUniqID.end()){
              basicBlockMapUniqID[*bi]= getInstructionIdreturn;
          }
           
         
          // fileID << basicBlockMapUniqID[*bi] << "\n";
          computeBackSlice(I, Chain);
          *Output << BBID << ',' << getInstructionIdreturn << ',' << CyclomaticNumber
                  << ',' << OviedoComplexity << ',' << Chain.size() << ','
                  << M.CmpSize << ',' << M.ComparesConstant << ','
                  << M.ComparesPointer << ',' << M.IsEquality << ','
                  << M.IsConstant << ',' << M.NumCases << '\n';
        }
        catch (...)
        {
          //skip this instruction, debug location unknown
          errs() << "exception caught";
          continue;
        }
      }
    }
  
  writeFunctionCFGtofile(F);
  
  }
  return false;
}

//function to get complexity
void StaticMetrics::getComplexity(Function const &F, unsigned &Cyclomatic,
                                  unsigned &Oviedo)
{
  unsigned EdgeCount = 0;
  unsigned DataFlowComplexity = 0;
  SmallSet<Value const *, 32> Locals;
  SmallSet<Value const *, 32> Foreigns;

  for (auto const &BB : F)
  {
    Locals.clear();
    Foreigns.clear();
    for (auto const &I : BB)
    {
      for (Use const &U : I.operands())
      {
        if (isa<BasicBlock>(U.get()))
          continue;
        if (isa<Constant>(U.get()))
          continue;
        if (Locals.count(U.get()))
          continue;
        Foreigns.insert(U.get());
      }
      Locals.insert(&I);
    }

    EdgeCount += BB.getTerminator()->getNumSuccessors();
    DataFlowComplexity += Foreigns.size();
  }

  Cyclomatic = EdgeCount - F.size() + 2;
  Oviedo = DataFlowComplexity + EdgeCount;
}

Value const *StaticMetrics::handleBranchCondition(Value const *V, Metrics &M)
{
  // Use dyn_cast_or_null as V can be from the following else branch
  if (auto *Phi = dyn_cast_or_null<PHINode>(V))
  {
    bool FirstSet = true;
    for (unsigned IncIdx = 0; IncIdx < Phi->getNumIncomingValues(); IncIdx++)
    {
      auto IncVal = Phi->getIncomingValue(IncIdx);
      if (isa<Constant>(IncVal))
        continue;

      Metrics MInc;
      if (!handleBranchCondition(IncVal, MInc))
        return nullptr;

      if (FirstSet)
      {
        M = MInc;
        FirstSet = false;
        continue;
      }

      M.CmpSize = std::max(MInc.CmpSize, M.CmpSize);
      M.ComparesConstant |= MInc.ComparesConstant;
      M.ComparesPointer |= MInc.ComparesPointer;
      M.IsEquality |= MInc.IsEquality;
      M.IsConstant = false;
    }

    return Phi;
  }
  else if (auto *BinOp = dyn_cast_or_null<BinaryOperator>(V))
  {
    auto *Operand0 = BinOp->getOperand(0);
    auto *Operand1 = BinOp->getOperand(1);

    Metrics M0, M1;
    auto *Val0 = handleBranchCondition(Operand0, M0);
    auto *Val1 = handleBranchCondition(Operand1, M1);

    if (!Val0 || !Val1)
      return nullptr;

    switch (BinOp->getOpcode())
    {
    case Instruction::BinaryOps::And:
      if (auto *ConstInt0 = dyn_cast<ConstantInt>(Val0))
      {
        bool Bool0 = ConstInt0->getValue().getBoolValue();

        if (auto *ConstInt1 = dyn_cast<ConstantInt>(Val1))
        {
          bool Bool1 = ConstInt1->getValue().getBoolValue();
          M = M0;
          // and true, true -> true
          if (Bool0 && Bool1)
            return Val0;
          // and true, false -> false
          if (Bool0)
            return Val1;
          // and false, * -> false
          return Val0;
        }

        if (Bool0)
        {
          // and true, %y -> %y
          M = M1;
          return Val1;
        }

        // and false, %y -> false
        M = M0;
        return Val0;
      }
      else if (auto *ConstInt1 = dyn_cast<ConstantInt>(Val1))
      {
        if (ConstInt1->getValue().getBoolValue())
        {
          // and %x, true -> %x
          M = M0;
          return Val0;
        }

        // and %x, false -> false
        M = M1;
        return Val1;
      }

      // neither operand is constant, aggregate according to `and` semantics
      M.CmpSize = M0.CmpSize + M1.CmpSize;
      M.ComparesConstant = M0.ComparesConstant && M1.ComparesConstant;
      M.ComparesPointer = M0.ComparesPointer && M1.ComparesPointer;
      M.IsEquality = M0.IsEquality && M1.IsEquality;
      M.IsConstant = M0.IsConstant && M1.IsConstant;

      return BinOp;

    case Instruction::BinaryOps::Or:
      if (auto *ConstInt0 = dyn_cast<ConstantInt>(Val0))
      {
        if (ConstInt0->getValue().getBoolValue())
        {
          // or true, %y -> true
          M = M0;
          return Val0;
        }

        // or false, %y -> %y
        M = M1;
        return Val1;
      }
      else if (auto *ConstInt1 = dyn_cast<ConstantInt>(Val1))
      {
        if (ConstInt1->getValue().getBoolValue())
        {
          // or %x, true -> true
          M = M1;
          return Val1;
        }

        // or %x, false -> %x
        M = M0;
        return Val0;
      }

      // neither operand is constant, aggregate according to `or` semantics
      M.CmpSize = std::max(M0.CmpSize, M1.CmpSize);
      M.ComparesConstant = M0.ComparesConstant || M1.ComparesConstant;
      M.ComparesPointer = M0.ComparesPointer || M1.ComparesPointer;
      M.IsEquality = M0.IsEquality || M1.IsEquality;
      M.IsConstant = false;

      return BinOp;

    case Instruction::BinaryOps::Xor:
      if (auto *ConstInt0 = dyn_cast<ConstantInt>(Val0))
      {
        bool Bool0 = ConstInt0->getValue().getBoolValue();

        if (auto *ConstInt1 = dyn_cast<ConstantInt>(Val1))
        {
          bool Bool1 = ConstInt1->getValue().getBoolValue();
          // xor when equal constants returns false
          if (Bool0 == Bool1)
          {
            if (Bool0)
            {
              M = M1;
              return ConstantInt::getFalse(BinOp->getType());
            }

            M = M0;
            return Val0;
          }
          else if (Bool0)
          {
            M = M0;
            return Val0;
          }

          M = M1;
          return Val1;
        }

        // xor *, %y -> %y
        M = M1;
        return Val1;
      }
      else if (M1.IsConstant)
      {
        // xor %x, * -> %x
        M = M0;
        return Val0;
      }

      // neither operand is constant, aggregate according to `xor` semantics
      M.CmpSize = std::max(M0.CmpSize, M1.CmpSize);
      M.ComparesConstant = M0.ComparesConstant || M1.ComparesConstant;
      M.ComparesPointer = M0.ComparesPointer || M1.ComparesPointer;
      M.IsEquality = M0.IsEquality || M1.IsEquality;
      M.IsConstant = false;

      return BinOp;

    default:
      UnhandledConditions++;
      LLVM_DEBUG(errs() << "Found unhandled binary operator\n"
                        << *Operand0 << '\n'
                        << *Operand1 << '\n'
                        << *BinOp << '\n');
    }

    return nullptr;
  }
  else if (auto *Select = dyn_cast_or_null<SelectInst>(V))
  {
    return handleBranchCondition(Select->getCondition(), M);
  }
  else if (V && (isa<LoadInst>(V) || isa<Constant>(V) ||
                 isa<Argument>(V) ||
                 isa<ExtractValueInst>(V) ||
                 isa<ExtractElementInst>(V)))
  {
    M.IsConstant = true;
  }
  else if (auto *Cast = dyn_cast_or_null<CastInst>(V))
  {
    M.CmpSize = Cast->getType()->getScalarSizeInBits();
    M.IsEquality = true;
  }
  else
  {
    if (V)
    {
      UnhandledConditions++;
      LLVM_DEBUG(errs() << "Found unhandled instruction\n"
                        << *V << '\n');
    }
    return nullptr;
  }

  return V;
}

void StaticMetrics::computeBackSlice(Instruction const *I,
                                     SmallVectorImpl<User const *> &Chain)
{
  SmallVector<Instruction const *, 8> Worklist;
  Worklist.push_back(I);

  Chain.clear();
  SmallSet<User const *, 32> Seen;
  while (!Worklist.empty())
  {
    auto User = Worklist.pop_back_val();
    Chain.push_back(User);
    Seen.insert(User);
    for (auto &Use : User->operands())
    {
      if (auto *I = dyn_cast<Instruction>(Use.get()))
      {
        if (!Seen.count(I))
          Worklist.push_back(I);
      }
    }
  }
}

// function to save the metrics to  the file
void StaticMetrics::print(raw_ostream &O, Module const *) const
{
  O << "Metrics have been stored into '"
    << "./static_analysis_results." << std::to_string(ModId).c_str() << ".out"
    << "'\n";
}

static void registerStaticAnalysisPass(const PassManagerBuilder &,
                                       legacy::PassManagerBase &PM)
{
  PM.add(new StaticMetrics());
}


// The pass named staticMetrics is registered
static RegisterPass<StaticMetrics> X("static-metrics",
                                     "Various complexity metrics",
                                     true /* Only looks at CFG */,
                                     true /* Analysis Pass */);

static RegisterStandardPasses
    RegisterStaticAnalysisPass(PassManagerBuilder::EP_OptimizerLast,
                               registerStaticAnalysisPass);

static RegisterStandardPasses
    RegisterStaticAnalysisPass0(PassManagerBuilder::EP_EnabledOnOptLevel0,
                                registerStaticAnalysisPass);
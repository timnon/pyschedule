using CP;

tuple Objective {
	key int task_id;
	float coefficient;
}

tuple Task {
	key int id;
	int length; 
}

tuple Resource {
	key int id;
    int capacity_low;
    int capacity_up;
}

tuple CumulResource {
	key int id;
	int resource_size;
}

tuple TaskCumulResource {
	key int task_id;
	key int resource_id;
	int resource_size_req;
}

tuple TaskResource {
	key int task_id;
	key int resource_id;
	int length;
	key int group_id;
}

// one group for every task-alternative
tuple TaskResourceGroup {
  	key int task_id;
  	key int group_id;
}

tuple TaskTaskResource {
    int task_id_1;
    int task_id_2;
    int resource_id;
}

tuple Precedence {
	int left_task;
	int right_task;
	int offset;
}

tuple Bound {
	int task;
	int bound;
}

tuple CapacityUp {
	key int capacity_up_id;
	int resource_id;
	int bound;
	int start;
	int end;
}

tuple CapacityUpTask {
	key int capacity_up_id;
	key int task_id;
	int req;
}


{Objective} Objectives = ...;
{Task} Tasks = ...;
{Resource} Resources = ...;
{CumulResource} CumulResources = ...;
{TaskCumulResource} TaskCumulResources = ...;
{TaskResource} TaskResources = ...;
{TaskResourceGroup} TaskResourceGroups = ...;
{TaskTaskResource} TaskTaskResources = ...;
{Precedence} Precedences = ...;
{Precedence} TightPrecedences = ...;
{Precedence} CondPrecedences = ...;
{Bound} UpperBounds = ...;
{Bound} LowerBounds = ...;
{Bound} FixBounds = ...;
{CapacityUp} CapacityUps = ...;
{CapacityUp} CapacitySliceUps = ...;
{CapacityUpTask} CapacityUpTasks = ...;



dvar interval Intervals[ T in Tasks ] size T.length;
dvar interval RIntervals[ TR in TaskResources ] optional size TR.length;
dvar sequence Resource_Seq[R in Resources] in all(TR in TaskResources : TR.resource_id == R.id) RIntervals[TR] types all(TR in TaskResources  : TR.resource_id == R.id) TR.task_id;
cumulFunction ResourceFunction[TCR in TaskCumulResources] = pulse(Intervals[<TCR.task_id>],TCR.resource_size_req) ;


execute {
	cp.param.FailLimit = 1000000;
}

minimize sum(T in Tasks ) sum( O in Objectives : O.task_id == T.id ) endOf(Intervals[T]) * O.coefficient;

subject to {

  forall (R in Resources)
  {
	   noOverlap(Resource_Seq[R],CondPrecedences);  
  }  

  forall( R in Resources )
  {
  	sum(TR in TaskResources) presenceOf(RIntervals[TR]) <= R.capacity_up;
  	sum(TR in TaskResources) presenceOf(RIntervals[TR]) >= R.capacity_low;
  } 

  forall (P in Precedences)
  {
     endOf(Intervals[ item(Tasks,P.left_task) ]) + P.offset <= startOf(Intervals[ item(Tasks,P.right_task) ]) ;
  }

  forall (P in TightPrecedences)
  {
     endOf(Intervals[ item(Tasks,P.left_task) ]) + P.offset == startOf(Intervals[ item(Tasks,P.right_task) ]) ;
  }
  
  forall (B in UpperBounds)
  {
     endOf(Intervals[ item(Tasks,B.task) ]) <= B.bound;    
  }
  
  forall (B in LowerBounds)
  {
     startOf(Intervals[ item(Tasks,B.task) ]) >= B.bound;    
  }

  forall (B in FixBounds)
  {
     startOf(Intervals[ item(Tasks,B.task) ]) == B.bound;    
  }
  
  forall(T in Tasks){
        forall( TRG in TaskResourceGroups : TRG.task_id == T.id ){
               		alternative(Intervals[T], all(TR in TaskResources : ( TR.group_id == TRG.group_id ) && ( TR.task_id == T.id ) ) RIntervals[TR]); // Resource Selection        
        }
  }

  forall(TR_1 in TaskResources){
        forall(TR_2 in TaskResources){
            forall(TTR in TaskTaskResources : ( TTR.task_id_1 == TR_1.task_id ) && ( TTR.task_id_2 == TR_2.task_id ) &&
                                              ( TTR.resource_id == TR_1.resource_id ) && ( TTR.resource_id == TR_2.resource_id ) ){
                presenceOf(RIntervals[TR_1]) >= presenceOf(RIntervals[TR_2]);
            }
        }
  }
  
  forall( PR in CumulResources ){
             sum( TCR in TaskCumulResources : TCR.resource_id == PR.id ) ResourceFunction[TCR] <= PR.resource_size; 
  }

  forall( CU in CapacityUps ){
        sum( CUT in CapacityUpTasks : CUT.capacity_up_id == CU.capacity_up_id, 
            TR in TaskResources : (TR.resource_id == CU.resource_id) && (TR.task_id == CUT.task_id) )
                          CUT.req*presenceOf(RIntervals[TR]) <= CU.bound;
  }

  forall( CU in CapacitySliceUps ){
        sum( CUT in CapacityUpTasks : CUT.capacity_up_id == CU.capacity_up_id, 
            TR in TaskResources : (TR.resource_id == CU.resource_id) && (TR.task_id == CUT.task_id) )
                          CUT.req*presenceOf(RIntervals[TR])*(startOf(RIntervals[TR])>=CU.start)*(endOf(RIntervals[TR])<=CU.end) <= CU.bound;
  }
};

// plot solution to log file
execute {
	write("##START_SOLUTION##");
	for ( var TR in TaskResources )
	{
		if ( RIntervals[TR].present == 1 )
		{
			write(TR.task_id,",",TR.resource_id,",",Intervals[ Tasks.get(TR.task_id) ].start,";");
		}
	}
	for ( TCR in TaskCumulResources )
	{
			write(TCR.task_id,",",TCR.resource_id,",",Intervals[ Tasks.get(TCR.task_id) ].start,";");
	}
	writeln("##END_SOLUTION##");
}





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
	int group_id;
}

// one group for every task-alternative
tuple TaskResourceGroup {
  	key int task_id;
  	key int group_id;
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


{Objective} Objectives = ...;
{Task} Tasks = ...;
{Resource} Resources = ...;
{CumulResource} CumulResources = ...;
{TaskCumulResource} TaskCumulResources = ...;
{TaskResource} TaskResources = ...;
{TaskResourceGroup} TaskResourceGroups = ...;
{Precedence} Precedences = ...;
{Precedence} TightPrecedences = ...;
{Precedence} CondPrecedences = ...;
{Bound} UpperBounds = ...;
{Bound} LowerBounds = ...;
{Bound} FixBounds = ...;



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
  
  forall( PR in CumulResources ){
             sum( TCR in TaskCumulResources : TCR.resource_id == PR.id ) ResourceFunction[TCR] <= PR.resource_size; 
  }

};

// plot solution to log file
execute {
	write("##START_SOLUTION##");
	for ( TR in TaskResources )
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
	write("##END_SOLUTION##");
}





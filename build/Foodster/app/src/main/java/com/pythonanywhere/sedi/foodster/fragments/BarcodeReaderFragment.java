package com.pythonanywhere.sedi.foodster.fragments;

import android.app.Activity;
import android.content.Context;
import android.content.Intent;
import android.content.SharedPreferences;
import android.os.AsyncTask;
import android.os.Bundle;
import android.support.v4.app.Fragment;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.TextView;
import android.widget.Toast;

import com.google.zxing.integration.android.IntentIntegrator;
import com.google.zxing.integration.android.IntentResult;
import com.pythonanywhere.sedi.foodster.R;
import com.pythonanywhere.sedi.foodster.models.JSONfunctions;
import com.pythonanywhere.sedi.foodster.models.ResponseWrapper;

public class BarcodeReaderFragment extends Fragment implements View.OnClickListener {

    public interface OnScanButtonClickedListener{
        public IntentResult askForResult();
        public boolean checkToProccess();
    }

    private Button scanButton;
    private OnScanButtonClickedListener mListener;

    public BarcodeReaderFragment(){
    }

    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
    }

    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container,
                             Bundle savedInstanceState) {
        View view = inflater.inflate(R.layout.fragment_barcode_reader, container, false);
        scanButton = (Button) view.findViewById(R.id.scan_button);
        scanButton.setOnClickListener(this);

        return view;
    }

    @Override
    public void onAttach(Context context) {
        super.onAttach(context);
        if (context instanceof OnScanButtonClickedListener) {
            mListener = (OnScanButtonClickedListener) context;
        } else {
            throw new RuntimeException(context.toString()
                    + " must implement OnFragmentInteractionListener");
        }
    }

    @Override
    public void onResume(){
        super.onResume();
        if(mListener.checkToProccess()){
//            processResult(mListener.askForResult());
            new ProcessResult().execute();
        }
    }

    @Override
    public void onClick(View v) {
        if(v.getId()==R.id.scan_button){
            IntentIntegrator scanIntegrator = new IntentIntegrator(getActivity());
            scanIntegrator.initiateScan();
        }
    }


//    public void onActivityResult(int requestCode, int resultCode, Intent intent){
//        System.out.println("Great!");
//
//        IntentResult scanningResult = IntentIntegrator.parseActivityResult(requestCode, resultCode, intent);
//
//        if(scanningResult != null){
//            String scanContent = scanningResult.getContents();
//            String scanFormat = scanningResult.getFormatName();
//            Toast toast = Toast.makeText(getActivity().getApplicationContext(),
//                    "Scan format: " + scanFormat + " ; Scan result: " + scanContent , Toast.LENGTH_LONG);
//            toast.show();
//        }
//    }

    private class ProcessResult extends AsyncTask<IntentResult, Void, Void> {

        @Override
        protected Void doInBackground(IntentResult... params) {

            SharedPreferences sharedPref
                    = getActivity().getSharedPreferences(getString(R.string.token_file_key), Context.MODE_PRIVATE);
            String token
                    = sharedPref.getString(getString(R.string.saved_token), getString(R.string.not_logged_status));

            ResponseWrapper response = JSONfunctions.getWithJSONResult(getString(R.string.product_list), token);
            System.out.print(response.toString());

            return null;
        }
    }
}
